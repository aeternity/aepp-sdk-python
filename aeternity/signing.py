import os

from hashlib import sha256

import base58
import rlp
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from ecdsa import SECP256k1, SigningKey
import ecdsa

# RLP version number
# https://github.com/aeternity/protocol/blob/epoch-v0.10.1/serializations.md#binary-serialization
VSN = 1

# The list of tags can be found here:
# https://github.com/aeternity/protocol/blob/epoch-v0.10.1/serializations.md#table-of-object-tags
TAG_SIGNED_TX = 11
TAG_SPEND_TX = 12


class SignableTransaction:

    def __init__(self, tx_json_data):
        self.tx_hash = tx_json_data['tx_hash']
        self.tx = tx_json_data['tx']
        self.tx_unsigned = base58.b58decode_check(tx_json_data['tx'][3:])
        self.tx_decoded = rlp.decode(self.tx_unsigned)

        # decode a transaction
        def btoi(byts):
            return int.from_bytes(byts, byteorder='big')

        self.tag = btoi(self.tx_decoded[0])
        self.vsn = btoi(self.tx_decoded[1])
        self.fields = {}
        if self.tag == TAG_SPEND_TX:
            self.fields['sender'] = base58.b58encode_check(self.tx_decoded[2])
            self.fields['recipient'] = base58.b58encode_check(self.tx_decoded[3])
            self.fields['amount'] = btoi(self.tx_decoded[4])
            self.fields['fee'] = btoi(self.tx_decoded[5])
            self.fields['nonce'] = btoi(self.tx_decoded[6])


class KeyPair:
    def __init__(self, signing_key, verifying_key):
        self.signing_key = signing_key
        self.verifying_key = verifying_key

    def get_address(self):
        """get the keypair public_key base58 encoded and prefixed (ak$...)"""
        pub_key = self.verifying_key.to_string()
        return 'ak$' + base58.b58encode_check(b'\x04' + pub_key)

    def get_private_key(self):
        """get the private key hex encoded"""
        return self.signing_key.to_string().hex()

    def sign_transaction_message(self, message):
        """sign a message with using the private key"""
        signature = self.signing_key.sign(message, sigencode=ecdsa.util.sigencode_der)
        return signature

    def sign_verify(self, message, signature):
        """verifify message signature, raise an error if the message cannot be verified"""
        assert self.verifying_key.verify(signature, message, sigdecode=ecdsa.util.sigdecode_der)

    def encode_transaction_message(self, unsigned_tx, signatures):
        """prepare a signed transaction message"""
        tag = bytes([TAG_SIGNED_TX])
        vsn = bytes([VSN])
        payload = rlp.encode([tag, vsn, signatures, unsigned_tx])
        return f"tx${base58.b58encode_check(payload)}"

    def sign_transaction(self, transaction):
        signature = self.sign_transaction_message(message=transaction.tx_unsigned)
        tx_encoded = self.encode_transaction_message(transaction.tx_unsigned, [signature])
        self.sign_verify(transaction.tx_unsigned, signature)
        b58_signature = 'sg$' + base58.b58encode_check(signature)
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
    def generate(cls):
        key = SigningKey.generate(curve=SECP256k1, hashfunc=sha256)
        return KeyPair(signing_key=key, verifying_key=key.get_verifying_key())

    @classmethod
    def from_public_private_key_strings(cls, public, private):
        """create a keypair from a aet address and private key string

        :param public: the aet address, used to verify the private key
        :param private: the hex encoded private key
        :return: a keypair object or raise error if the public key doesnt match
        """
        pk = bytes.fromhex(private)
        signing_key = SigningKey.from_string(pk, curve=SECP256k1, hashfunc=sha256)
        kp = KeyPair(signing_key, signing_key.get_verifying_key())
        assert kp.get_address() == public
        return kp

    @classmethod
    def sha256(cls, data):
        hash = SHA256.new()
        hash.update(data)
        return hash.digest()

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
