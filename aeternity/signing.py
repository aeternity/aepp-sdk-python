import os

import base58
import rlp
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
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


def _base58_decode(encoded):
    """decode a base58 epoch string to bytes
    it works with all the string like tx$..., sg$..., ak$....
    """
    if encoded[2] != '$':
        raise ValueError('Invalid hash')
    return base58.b58decode_check(encoded[3:])


def _base58_encode(prefix, data):
    """crete a base58 encoded string with a prefix, ex: ak$encoded_data, th$encoded_data,..."""
    return f"{prefix}${base58.b58encode_check(data)}"


class KeyPair:
    """Implement private/public key functionalities"""

    def __init__(self, signing_key, verifying_key):
        self.signing_key = signing_key
        self.verifying_key = verifying_key

    def get_address(self):
        """get the keypair public_key base58 encoded and prefixed (ak$...)"""
        pub_key = self.verifying_key.encode(encoder=nacl.encoding.RawEncoder)
        return _base58_encode("ak", pub_key)

    def get_private_key(self):
        """get the private key hex encoded"""
        return self.signing_key.to_string().hex()

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
        return _base58_encode("tx", payload)

    def sign_transaction(self, transaction):
        """sign a transaction"""
        tx_decoded = _base58_decode(transaction.tx)
        signature = self.signing_key.sign(tx_decoded).signature
        # self.sign_verify(tx_decoded, signature)
        # encode the transaction message with the signature
        tx_encoded = self.encode_transaction_message(tx_decoded, [signature])
        b58_signature = _base58_encode("sg", signature)
        return tx_encoded, b58_signature

    def save_to_folder(self, folder, password):
        enc_key = self._encrypt_key(self.signing_key.to_string(), password)
        enc_key_pub = self._encrypt_key(self.verifying_key.to_string(), password)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(os.path.join(folder, 'key'), 'wb') as fh:
            fh.write(enc_key)
        with open(os.path.join(folder, 'key.pub'), 'wb') as fh:
            fh.write(enc_key_pub)

    #
    # initializers
    #

    @classmethod
    def compute_tx_hash(cls, singed_transaction):
        """
        generate the hash from a signed and encoded transaction
        :param signed_transaction: a encoded signed transaction
        """
        signed = _base58_decode(singed_transaction)
        return _base58_encode("th", blake2b(data=signed, digest_size=32, encoder=nacl.encoding.RawEncoder))

    @classmethod
    def generate(cls):
        signing_key = SigningKey.generate()
        return KeyPair(signing_key=signing_key, verifying_key=signing_key.verify_key)

    @classmethod
    def from_public_private_key_strings(cls, public, private):
        """create a keypair from a aet address and private key string

        :param public: the aet address, used to verify the private key
        :param private: the hex encoded private key
        :return: a keypair object or raise error if the public key doesnt match
        """
        k = bytes.fromhex(private)
        # the private key string is composed with [private_key+pyblic_key]
        # https://blog.mozilla.org/warner/2011/11/29/ed25519-keys/
        signing_key = SigningKey(seed=k[0:32], encoder=encoding.RawEncoder)
        kp = KeyPair(signing_key, signing_key.verify_key)
        assert kp.get_address() == public
        return kp

    @classmethod
    def _encrypt_key(cls, key_string, password):
        if isinstance(password, str):
            password = password.encode('utf-8')
        aes = AES.new(cls.sha256(password))
        encrypted_key = aes.encrypt(key_string)
        return encrypted_key

    @classmethod
    def _decrypt_key(cls, key_content, password):
        if isinstance(password, str):
            password = password.encode('utf-8')
        aes = AES.new(cls.sha256(password))
        decrypted_key = aes.decrypt(key_content)
        return decrypted_key

    @classmethod
    def read_from_files(cls, public_key_file, private_key_file, password):
        with open(public_key_file, 'rb') as fh:
            public = cls._decrypt_key(fh.read(), password)
        with open(private_key_file, 'rb') as fh:
            private = cls._decrypt_key(fh.read(), password)
        return KeyPair.from_public_private_key_strings(public, private)

    @classmethod
    def read_from_dir(cls, directory, password):
        return cls.read_from_files(
            os.path.join(directory, 'key.pub'),
            os.path.join(directory, 'key'),
            password
        )

    @classmethod
    def sha256(cls, data):
        hash = SHA256.new()
        hash.update(data)
        return hash.digest()
