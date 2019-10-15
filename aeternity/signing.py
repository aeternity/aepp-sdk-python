import os
from datetime import datetime
import json
import uuid

from nacl.encoding import RawEncoder, HexEncoder
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import CryptoError
from nacl.pwhash import argon2id
from nacl import secret, utils as nacl_utils
from aeternity.identifiers import ACCOUNT_ID, ACCOUNT_API_FORMAT, ACCOUNT_SOFIA_FORMAT, ACCOUNT_RAW_FORMAT
from aeternity.identifiers import ACCOUNT_KIND_BASIC
from aeternity import hashing, utils


class Account:
    """Implement secret/public key functionalities"""

    def __init__(self, signing_key, verifying_key, **kwargs):
        # distinguish from poa / ga
        # TODO: handle the case that they are not set
        self.nonce = kwargs.get("nonce", 0)
        self.balance = kwargs.get("balance", 0)
        self.kind = kwargs.get("kind", ACCOUNT_KIND_BASIC)
        self.contract_id = kwargs.get("contract_id")
        self.auth_fun = kwargs.get("auth_fun")
        self.address = kwargs.get("id")
        self.signing_key = signing_key
        self.verifying_key = verifying_key
        if verifying_key is not None:
            pub_key = self.verifying_key.encode(encoder=RawEncoder)
            self.address = hashing.encode(ACCOUNT_ID, pub_key)

    def get_address(self, format=ACCOUNT_API_FORMAT):
        """
        Get the account address
        :param format: the format of the address, possible values are 'api', 'sofia', 'raw', default is 'api'

        when the format is:
        - api the address is base58 encoded with ak_ as prefix
        - sofia the addres is hex encoded with 0x as prefix
        - raw the address is returned as a byte array

        raise ValueError when the format is not recognized
        """
        if format == ACCOUNT_API_FORMAT or format is None:
            return self.address
        elif format == ACCOUNT_RAW_FORMAT:
            return self.verifying_key.encode()
        elif format == ACCOUNT_SOFIA_FORMAT:
            return f'0x{self.verifying_key.encode(encoder=HexEncoder).decode("utf-8")}'
        raise ValueError(f'Unrecognized format {format} for address encoding')

    def get_secret_key(self) -> str:
        """
        Get the secret key as a hex encoded string
        """
        sk = self.signing_key.encode(encoder=HexEncoder).decode('utf-8')
        pk = self.verifying_key.encode(encoder=HexEncoder).decode('utf-8')
        return f"{sk}{pk}"

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

    def is_generalized(self):
        """
        Tells wherever the account is a generalized.
        An account is generalized if it has the kind = generalized
        :return: true if it is generalized, false if it is basic
        """
        if self.kind == ACCOUNT_KIND_BASIC:
            return False
        return True

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
        if utils.is_valid_hash(key_string, prefix=ACCOUNT_ID):
            return hashing.decode(key_string.strip())
        return bytes.fromhex(key_string.strip())

    @classmethod
    def from_private_key_string(cls, key_string):
        """
        Deprecated version for Account.from_secret_key_string
        """
        return Account.from_secret_key_string(key_string)

    @classmethod
    def from_secret_key_string(cls, key_string):
        """create a keypair from a chain address and key_string key string
        :param key_string: the encoded key_string key (hex for private, prefixed base58 for public)
        :return: a keypair object or raise error if the public key doesn't match
        """
        k = cls._raw_key(key_string)
        # the secret key string is composed with [secret_key+public_key]
        # https://blog.mozilla.org/warner/2011/11/29/ed25519-keys/
        signing_key = SigningKey(seed=k[0:32], encoder=RawEncoder)
        kp = Account(signing_key, signing_key.verify_key)
        return kp

    @classmethod
    def from_node_api(cls, api_account, secret_key=None):
        """
        Load an account from the object returned by the node API
        endpoint get_accounts_from_pubkey (/accounts/{pubkey}),
        and optionally passing a secret key for signing.
        The secret key must match the account address (pubkey)
        :param api_account: the account object obtained from the node api
        :param secret_key: optional secret key to allow signing
        """
        # TODO: the account api is a bit convoluted, could be simplified
        # api_account is namedtuple of type Account returned by the node

        account = Account(None, None, **api_account._asdict())
        if secret_key is not None:
            account.signing_key = cls._raw_key(secret_key)
            # TODO: is this test relevant?
            if account.get_address() != api_account.account_id:
                raise ValueError(f"Public key mismatch, expected {api_account.account_id} got {account.get_address()}")
        return account

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


def keystore_seal(secret_key, password, address, name=""):
    """
    Seal a keystore

    :param secret_key: the secret key to store in the keystore
    :param password: the keystore password
    :param address: the address
    :param name: the optional name of the keystore
    """
    # password
    salt = nacl_utils.random(argon2id.SALTBYTES)
    mem = argon2id.MEMLIMIT_MODERATE
    ops = argon2id.OPSLIMIT_MODERATE
    key = argon2id.kdf(secret.SecretBox.KEY_SIZE, password.encode(), salt, opslimit=ops, memlimit=mem)
    # ciphertext
    box = secret.SecretBox(key)
    nonce = nacl_utils.random(secret.SecretBox.NONCE_SIZE)
    sk = secret_key.encode(encoder=RawEncoder) + secret_key.verify_key.encode(encoder=RawEncoder)
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
                "parallelism": 1  # pynacl 1.3.0 doesn't support this parameter
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
    # pynacl 1.3.0 doesn't support this parameter and can only use 1
    if par != 1:
        raise ValueError(f"Invalid parallelism {par} value, only parallelism = 1 is supported in the python sdk")
    key = argon2id.kdf(secret.SecretBox.KEY_SIZE, password.encode(), salt, opslimit=ops, memlimit=mem)
    # decrypt
    box = secret.SecretBox(key)
    nonce = bytes.fromhex(k.get("crypto", {}).get("cipher_params", {}).get("nonce"))
    encrypted = bytes.fromhex(k.get("crypto", {}).get("ciphertext"))
    private_key = box.decrypt(encrypted, nonce=nonce, encoder=RawEncoder)
    return private_key


def is_signature_valid(account_id, signature, data: bytes) -> bool:
    """
    Verify the signature of a message
    :param account_id: the account id signing the message
    :param signature: the signature of the message
    :param data: the message that has been signed
    :return: true if the signature for the message is valid, false otherwise
    """
    try:
        id = hashing.decode(account_id) if isinstance(account_id, str) else account_id
        sg = hashing.decode(signature) if isinstance(signature, str) else signature
        VerifyKey(id).verify(data, sg)
        return True
    except Exception:
        return False
