import os
import pathlib
from datetime import datetime
import json
import uuid

from nacl.encoding import RawEncoder, HexEncoder
from nacl.signing import SigningKey
from nacl.exceptions import CryptoError
from nacl.pwhash import argon2id
from nacl import secret, utils as nacl_utils


from aeternity import hashing, utils


class Account:
    """Implement private/public key functionalities"""

    def __init__(self, signing_key, verifying_key):
        self.signing_key = signing_key
        self.verifying_key = verifying_key
        pub_key = self.verifying_key.encode(encoder=RawEncoder)
        self.address = hashing.encode("ak", pub_key)

    def get_address(self):
        """get the keypair public_key base58 encoded and prefixed (ak_...)"""
        return self.address

    def get_private_key(self):
        """get the private key hex encoded"""
        pk = self.signing_key.encode(encoder=HexEncoder).decode('utf-8')
        pb = self.verifying_key.encode(encoder=HexEncoder).decode('utf-8')
        return f"{pk}{pb}"

    def sign(self, data):
        """
        Sign data
        :param data: the data to sign
        :return: the signature of the data
        """
        return self.signing_key.sign(data).signature

    def verify(self, data, signature):
        """
        Verify data signature, raise an error if the signature cannot be verified
        :param data: the data
        :param signature: the signature to verify
        """
        self.verifying_key.verify(signature, data)

    def save_to_keystore_file(self, path, password):
        """
        Utility method for save_to_keystore
        """
        folder = os.path.dirname(path)
        filename = os.path.basename(path)
        self.save_to_keystore(folder, password, filename=filename)

    def save_to_keystore(self, path, password, filename=None):
        """
        Save an account in a Keystore/JSON format
        :param path: the folder where to store the keystore file
        :param password: the password for the keystore
        :param filename: an optional filename to use for the keystore (default to UTC--ISO8601Date--AccountAddress)
        :return: the filename that has been used for the keystore
        """
        if filename is None:
            filename = f"UTC--{datetime.utcnow().isoformat()}--{self.get_address()}"
        with open(os.open(os.path.join(path, filename), os.O_TRUNC | os.O_CREAT | os.O_WRONLY, 0o600), 'w') as fp:
            j = keystore_seal(self.signing_key, password, self.get_address())
            json.dump(j, fp)
        return filename

    def save_to_folder(self, folder, password, name='key'):
        """
        save the current key in a folder and encrypts it with the provided password
        :param folder:   the folder to save the key to
        :param password: the password to encrypt the private key
        :param name:     filename of the signing key in folder, default 'key'
        """
        enc_key = self._encrypt_key(self.signing_key.encode(encoder=HexEncoder), password)
        enc_key_pub = self._encrypt_key(self.verifying_key.encode(encoder=HexEncoder), password)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(os.path.join(folder, name), 'wb') as fh:
            fh.write(enc_key)
        with open(os.path.join(folder, f'{name}.pub'), 'wb') as fh:
            fh.write(enc_key_pub)

    def save_to_file(self, path, password):
        p = pathlib.Path(path)
        folder = str(p.parent)
        filename = p.name
        self.save_to_folder(folder, password, name=filename)

    #
    # initializers
    #

    @classmethod
    def generate(cls):
        signing_key = SigningKey.generate()
        return Account(signing_key=signing_key, verifying_key=signing_key.verify_key)

    @classmethod
    def _raw_key(cls, key_string):
        """decode a key with different method between signing and addresses"""
        key_string = str(key_string)
        if utils.is_valid_hash(key_string, prefix='ak'):
            return hashing.decode(key_string.strip())
        return bytes.fromhex(key_string.strip())

    @classmethod
    def from_private_key_string(cls, key_string):
        """create a keypair from a aet address and key_string key string
        :param key_string: the encoded key_string key (hex for private, prefixed base58 for public)
        :return: a keypair object or raise error if the public key doesnt match
        """
        k = cls._raw_key(key_string)
        # the private key string is composed with [private_key+public_key]
        # https://blog.mozilla.org/warner/2011/11/29/ed25519-keys/
        signing_key = SigningKey(seed=k[0:32], encoder=RawEncoder)
        kp = Account(signing_key, signing_key.verify_key)
        return kp

    @classmethod
    def from_keystore(cls, path, password):
        """
        Load an account from a Keystore/JSON file
        :param path: the path to the keystore
        :param password: the password to decrypt the keystore
        :return: the account

        raise an error if the account cannot be opened

        """
        try:
            with open(path) as fp:
                j = json.load(fp)
                raw_private_key = keystore_open(j, password)
                signing_key = SigningKey(seed=raw_private_key[0:32], encoder=RawEncoder)
                kp = Account(signing_key, signing_key.verify_key)
                return kp
        except CryptoError as e:
            raise ValueError(e)

    @classmethod
    def from_public_private_key_strings(cls, public, private):
        """
        Create a keypair from a aet address and private key string

        :param public:  the aet address, used to verify the private key
        :param private: the hex encoded private key
        :return:        a keypair object or raise error if the public key doesnt match
        """
        kp = cls.from_private_key_string(private)
        if kp.get_address() != public:
            raise ValueError("Public key and private account mismatch")
        return kp


def keystore_seal(private_key, password, address, name=""):
    # password
    salt = nacl_utils.random(argon2id.SALTBYTES)
    mem = argon2id.MEMLIMIT_MODERATE
    ops = argon2id.OPSLIMIT_MODERATE
    key = argon2id.kdf(secret.SecretBox.KEY_SIZE, password.encode(), salt, opslimit=ops, memlimit=mem)
    # ciphertext
    box = secret.SecretBox(key)
    nonce = nacl_utils.random(secret.SecretBox.NONCE_SIZE)
    sk = private_key.encode(encoder=RawEncoder) + private_key.verify_key.encode(encoder=RawEncoder)
    ciphertext = box.encrypt(sk, nonce=nonce).ciphertext
    # build the keystore
    k = {
        "public_key": address,
        "crypto": {
            "secret_type": "ed25519",
            "symmetric_alg": "xsalsa20-poly1305",
            "ciphertext": bytes.hex(ciphertext),
            "cipher_params": {
                "nonce": bytes.hex(nonce)
            },
            "kdf": "argon2id",
            "kdf_params": {
                "memlimit_kib": round(mem / 1024),
                "opslimit": ops,
                "salt": bytes.hex(salt),
                "parallelism": 1  # pynacl 1.3.0 doesnt support this parameter
            }
        },
        "id": str(uuid.uuid4()),
        "name": name,
        "version": 1
    }
    return k


def keystore_open(k, password):
    # password
    salt = bytes.fromhex(k.get("crypto", {}).get("kdf_params", {}).get("salt"))
    ops = k.get("crypto", {}).get("kdf_params", {}).get("opslimit")
    mem = k.get("crypto", {}).get("kdf_params", {}).get("memlimit_kib") * 1024
    par = k.get("crypto", {}).get("kdf_params", {}).get("parallelism")
    # pynacl 1.3.0 doesnt support this parameter and can only use 1
    if par != 1:
        raise ValueError(f"Invalid parallelism {par} value, only parallelism = 1 is supported in the python sdk")
    key = argon2id.kdf(secret.SecretBox.KEY_SIZE, password.encode(), salt, opslimit=ops, memlimit=mem)
    # decrypt
    box = secret.SecretBox(key)
    nonce = bytes.fromhex(k.get("crypto", {}).get("cipher_params", {}).get("nonce"))
    encrypted = bytes.fromhex(k.get("crypto", {}).get("ciphertext"))
    private_key = box.decrypt(encrypted, nonce=nonce, encoder=RawEncoder)
    return private_key
