import math
import base58
import rlp
import secrets
from nacl.hash import blake2b
from nacl.encoding import RawEncoder

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def _base58_decode(encoded_str):
    """decode a base58 string to bytes"""
    return base58.b58decode_check(encoded_str)


def _base58_encode(data):
    """create a base58 encoded string"""
    return base58.b58encode_check(data)


def _blacke2b_digest(data):
    """create a blacke2b 32 bit raw encoded digest"""
    return blake2b(data=data, digest_size=32, encoder=RawEncoder)


def _sha256(data):
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(data)
    return digest.finalize()


def encode(prefix, data):
    """encode data using the default encoding/decoding algorithm and prepending the prefix with a prefix, ex: ak_encoded_data, th_encoded_data,..."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return f"{prefix}_{base58.b58encode_check(data)}"


def decode(data):
    """
    Decode data using the default encoding/decoding algorithm
    :param data: a encoded and prefixed string (ex tx_..., sg_..., ak_....)
    :return: the raw byte array of the decoded hashed
    """

    if data is None or len(data.strip()) < 3 or data[2] != '_':
        raise ValueError('Invalid hash')
    return _base58_decode(data[3:])


def encode_rlp(prefix, data):
    """
    Encode an array in rlp format
    :param prefix: the prefix to use in the encoded string
    :param data: the array that has to be encoded in rlp
    """
    if not isinstance(data, list):
        raise ValueError("data to be encoded to rlp must be an array")
    payload = rlp.encode(data)
    return encode(prefix, payload)


def hash(data):
    """run the default hashing algorithm"""
    return _blacke2b_digest(data)


def hash_encode(prefix, data):
    """run the default hashing + digest algorithms"""
    return encode(prefix, hash(data))


def namehash(name):
    if isinstance(name, str):
        name = name.encode('ascii')
    # see:
    # https://github.com/aeternity/protocol/blob/master/AENS.md#hashing
    # and also:
    # https://github.com/ethereum/EIPs/blob/master/EIPS/eip-137.md#namehash-algorithm
    labels = name.split(b'.')
    hashed = b'\x00' * 32
    while labels:
        hashed = hash(hashed + hash(labels[0]))
        labels = labels[1:]
    return hashed


def namehash_encode(prefix, name):
    return encode(prefix, namehash(name))


def randint():
    return secrets.randbelow(2**64)


def to_bytes(val):
    """
    Encode a value to bytes.
    If the value is an int it will be encoded as bytes big endian
    Raises ValueError if the input is not an int or string
    """
    if isinstance(val, int):
        s = int(math.ceil(val.bit_length() / 8))
        return val.to_bytes(s, 'big')
    if isinstance(val, str):
        return val.encode("utf-8")
    if isinstance(val, bytes):
        return val
    raise ValueError("Byte serialization not supported")
