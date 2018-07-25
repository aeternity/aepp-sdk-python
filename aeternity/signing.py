import os
import pathlib
import base58
import rlp
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import nacl
from nacl import encoding
from nacl.signing import SigningKey
from nacl.hash import blake2b

# RLP version number
# https://github.com/aeternity/protocol/blob/epoch-v0.10.1/serializations.md#binary-serialization
VSN = 1

# The list of tags can be found here:
# https://github.com/aeternity/protocol/blob/epoch-v0.10.1/serializations.md#table-of-object-tags
TAG_SIGNED_TX = 11
TAG_SPEND_TX = 12


def _base58_decode(encoded_str):
    """decode a base58 string to bytes"""
    return base58.b58decode_check(encoded_str)


def _base58_encode(data):
    """crete a base58 encoded string"""
    return base58.b58encode_check(data)


def _blacke2b_digest(data):
    """create a blacke2b 32 bit raw encoded digest"""
    return blake2b(data=data, digest_size=32, encoder=nacl.encoding.RawEncoder)


def encode(prefix, data):
    """encode data using the default encoding/decoding algorithm and prepending the prefix with a prefix, ex: ak$encoded_data, th$encoded_data,..."""
    return f"{prefix}${base58.b58encode_check(data)}"


def decode(data):
    """decode data using the default encoding/decoding algorithm
    :param data: a encoded and prefixed string (ex tx$..., sg$..., ak$....)
    """
    if data[2] != '$':
        raise ValueError('Invalid hash')
    return _base58_decode(data[3:])


def hash(data):
    """run the default hashing algorihtm"""
    return _blacke2b_digest(data)


def hash_encode(prefix, data):
    """run the default hashing + digest algorihtms"""
    return encode(prefix, hash(data))


class KeyPair:
    """Implement private/public key functionalities"""

    def __init__(self, signing_key, verifying_key):
        self.signing_key = signing_key
        self.verifying_key = verifying_key

    def get_address(self):
        """get the keypair public_key base58 encoded and prefixed (ak$...)"""
        pub_key = self.verifying_key.encode(encoder=nacl.encoding.RawEncoder)
        return encode("ak", pub_key)

    def get_private_key(self):
        """get the private key hex encoded"""
        pk = self.signing_key.encode(encoder=nacl.encoding.HexEncoder).decode('utf-8')
        pb = self.verifying_key.encode(encoder=nacl.encoding.HexEncoder).decode('utf-8')
        return f"{pk}{pb}"

    def sign_transaction_message(self, message):
        """sign a message with using the private key"""
        return self.signing_key.sign(message).signature

    def sign_verify(self, message, signature):
        """verify message signature, raise an error if the message cannot be verified"""
        assert self.verifying_key.verify(signature, message)

    def encode_transaction_message(self, unsigned_tx, signatures):
        """prepare a signed transaction message"""
        tag = bytes([TAG_SIGNED_TX])
        vsn = bytes([VSN])
        payload = rlp.encode([tag, vsn, signatures, unsigned_tx])
        return encode("tx", payload)

    def sign_transaction(self, transaction):
        """sign a transaction"""
        tx_decoded = decode(transaction.tx)
        signature = self.signing_key.sign(tx_decoded).signature
        # self.sign_verify(tx_decoded, signature)
        # encode the transaction message with the signature
        tx_encoded = self.encode_transaction_message(tx_decoded, [signature])
        b58_signature = encode("sg", signature)
        return tx_encoded, b58_signature

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
    def compute_tx_hash(cls, singed_transaction):
        """
        generate the hash from a signed and encoded transaction
        :param signed_transaction: a encoded signed transaction
        """
        signed = decode(singed_transaction)
        return hash_encode("th", signed)

    @classmethod
    def generate(cls):
        signing_key = SigningKey.generate()
        return KeyPair(signing_key=signing_key, verifying_key=signing_key.verify_key)

    @classmethod
    def _raw_key(cls, key_string):
        """decode a key with different method between signing and addresses"""
        key_string = str(key_string)
        if key_string.startswith('ak$'):
            return decode(key_string.strip())
        return bytes.fromhex(key_string.strip())

    @classmethod
    def from_private_key_string(cls, key_string):
        """create a keypair from a aet address and key_string key string
        :param key_string: the encoded key_string key (hex for private, prefixed base58 for public)
        :return: a keypair object or raise error if the public key doesnt match
        """
        k = cls._raw_key(key_string)
        # the private key string is composed with [private_key+pyblic_key]
        # https://blog.mozilla.org/warner/2011/11/29/ed25519-keys/
        signing_key = SigningKey(seed=k[0:32], encoder=encoding.RawEncoder)
        kp = KeyPair(signing_key, signing_key.verify_key)
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
        assert kp.get_address() == public
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

        key = cls.sha256(password)
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

        key = cls.sha256(password)
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
        return KeyPair.from_public_private_key_strings(public, private)

    @classmethod
    def read_from_private_key(cls, private_key_file, password=None):
        with open(private_key_file, 'rb') as fh:
            private = cls._decrypt_key(fh.read(), password)
        return KeyPair.from_private_key_string(private)

    @classmethod
    def read_from_dir(cls, directory, password, name='key'):
        return cls.read_from_files(
            os.path.join(directory, f'{name}.pub'),
            os.path.join(directory, name),
            password
        )

    @classmethod
    def sha256(cls, data):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(data)
        return digest.finalize()
