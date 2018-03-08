import os
from collections import namedtuple

from hashlib import sha256

import base58
import msgpack
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from ecdsa import SECP256k1, SigningKey, VerifyingKey
import ecdsa


class SignableTransaction:
    def __init__(self, tx_json_data):
        self.tx_json_data = tx_json_data
        self.tx_msg_packed = base58.b58decode_check(tx_json_data['tx'][3:])
        self.tx_unpacked = msgpack.unpackb(self.tx_msg_packed)


class KeyPair:
    def __init__(self, signing_key, verifying_key):
        self.signing_key = signing_key
        self.verifying_key = verifying_key

    def get_address(self):
        pub_key = self.verifying_key.to_string()
        return 'ak$' + base58.b58encode_check(b'\x04' + pub_key)

    def encode_transaction_message(self, unpacked_tx, signatures):
        if not isinstance(signatures, list):
            signatures = [signatures]
        message = [
            b"sig_tx",  # SIG_TX_TYPE
            1,          # VSN
            unpacked_tx,
            signatures
        ]
        str = base58.b58encode_check(msgpack.packb(message, use_bin_type=True))
        return "tx$" + str

    def sign_transaction_message(self, msgpacked_tx):
        return self.signing_key.sign(msgpacked_tx, sigencode=ecdsa.util.sigencode_der)

    def sign_transaction(self, transaction):
        signature = self.sign_transaction_message(msgpacked_tx=transaction.tx_msg_packed)
        encoded_msg = self.encode_transaction_message(transaction.tx_unpacked, [signature])
        b58_signature = 'sg$' + base58.b58encode_check(signature)
        return encoded_msg, b58_signature

    def save_to_folder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(os.path.join(folder, 'key'), 'wb') as fh:
            fh.write(self.signing_key.to_string())
        with open(os.path.join(folder, 'key.pub'), 'wb') as fh:
            fh.write(self.verifying_key.to_string())

    #
    # initializers
    #

    @classmethod
    def generate(cls):
        key = SigningKey.generate(curve=SECP256k1, hashfunc=sha256)
        return KeyPair(signing_key=key, verifying_key=key.get_verifying_key())

    @classmethod
    def from_public_private_key_strings(cls, public, private):
        signing_key = SigningKey.from_string(private, curve=SECP256k1, hashfunc=sha256)
        return KeyPair(signing_key, signing_key.get_verifying_key())

    @classmethod
    def sha256(cls, data):
        hash = SHA256.new()
        hash.update(data)
        return hash.digest()

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
