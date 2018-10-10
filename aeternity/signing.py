import os
import pathlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import nacl
from nacl.encoding import RawEncoder
from nacl.signing import SigningKey
from aeternity import hashing, utils
# imports for keystore
from datetime import datetime
import eth_keyfile as keystore
import json


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
        pk = self.signing_key.encode(encoder=nacl.encoding.HexEncoder).decode('utf-8')
        pb = self.verifying_key.encode(encoder=nacl.encoding.HexEncoder).decode('utf-8')
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
        j = keystore.create_keyfile_json(self.signing_key.encode(encoder=RawEncoder), password.encode("utf-8"))
        if filename is None:
            filename = f"UTC--{datetime.utcnow().isoformat()}--{self.get_address()}"
        with open(os.path.join(path, filename), 'w') as fp:
            json.dump(j, fp)
        return filename

    @staticmethod
    def load_from_keystore(path, password):
        """
        Load an account from a Keystore/JSON file
        :param path: the path to the keystore
        :param password: the password to decrypt the keystore
        :return: the account

        raise an error if the account cannot be opened

        """
        with open(path, 'r') as fp:
            j = json.load(fp)
            raw_priv = keystore.decode_keyfile_json(j, password.encode("utf-8"))
            signing_key = SigningKey(seed=raw_priv[0:32], encoder=RawEncoder)
            kp = Account(signing_key, signing_key.verify_key)
            return kp

    def save_to_folder(self, folder, password, name='key'):
        """
        save the current key in a folder and encrypts it with the provided password
        :param folder:   the folder to save the key to
        :param password: the password to encrypt the private key
        :param name:     filename of the signing key in folder, default 'key'
        """
        enc_key = self._encrypt_key(self.signing_key.encode(encoder=nacl.encoding.HexEncoder), password)
        enc_key_pub = self._encrypt_key(self.verifying_key.encode(encoder=nacl.encoding.HexEncoder), password)
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

    @classmethod
    def _encrypt_key(cls, key_hexstring, password):
        """
        Encrypt a signing key string with the provided password

        :param key:        the key to encode in hex string
        :param password:   the password to use for encryption
        """
        if isinstance(password, str):
            password = password.encode('utf-8')

        key = hashing._sha256(password)
        encryptor = Cipher(
            algorithms.AES(key),
            modes.ECB(),
            backend=default_backend()
        ).encryptor()
        encrypted_key = encryptor.update(key_hexstring) + encryptor.finalize()
        return encrypted_key

    @classmethod
    def _decrypt_key(cls, key_content, password):
        """
        Decrypt a key using password
        :return: the string that was encrypted
        """
        if isinstance(password, str):
            password = password.encode('utf-8')

        key = hashing._sha256(password)
        decryptor = Cipher(
            algorithms.AES(key),
            modes.ECB(),
            backend=default_backend()
        ).decryptor()

        decrypted_key = decryptor.update(key_content) + decryptor.finalize()
        return decrypted_key.decode("utf-8")

    @classmethod
    def read_from_files(cls, public_key_file, private_key_file, password):
        with open(public_key_file, 'rb') as fh:
            public = cls._decrypt_key(fh.read(), password)
        with open(private_key_file, 'rb') as fh:
            private = cls._decrypt_key(fh.read(), password)
        return Account.from_public_private_key_strings(public, private)

    @classmethod
    def read_from_private_key(cls, private_key_file, password=None):
        with open(private_key_file, 'rb') as fh:
            private = cls._decrypt_key(fh.read(), password)
        return Account.from_private_key_string(private)

    @classmethod
    def read_from_dir(cls, directory, password, name='key'):
        return cls.read_from_files(
            os.path.join(directory, f'{name}.pub'),
            os.path.join(directory, name),
            password
        )
