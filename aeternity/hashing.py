import base58
import base64
import hashlib
import rlp
import secrets
import math

from nacl.hash import blake2b
from nacl.encoding import RawEncoder

from aeternity import identifiers


def _base58_encode(data):
    """create a base58 encoded string with checksum"""
    return base58.b58encode_check(data)


def _base58_decode(encoded_str):
    """decode a base58 with checksum string to bytes"""
    return base58.b58decode_check(encoded_str)


def _checksum(data: bytes) -> bytes:
    """
    Compute a 4 bytes checksum of the input data
    """
    return _sha256(_sha256(data))[:4]


def _base64_encode(data: bytes) -> str:
    """create a base64 encoded string with checksum"""
    return base64.b64encode(data + _checksum(data)).decode()


def _base64_decode(encoded_str: str) -> bytes:
    """decode a base64 with checksum string to bytes"""
    # check for none
    if encoded_str is None:
        raise ValueError("Invalid input for base64 decode check")
    # decode bytes
    raw = base64.b64decode(encoded_str)
    # check size
    if len(raw) < 5:
        raise ValueError("Invalid input for base64 decode check")
    # test checksum
    data, check = raw[:-4], raw[-4:]
    if check != _checksum(data):
        raise ValueError("Checksum mismatch when decoding base64 hash")
    return data


def _blacke2b_digest(data):
    """create a blacke2b 32 bit raw encoded digest"""
    return blake2b(data=data, digest_size=32, encoder=RawEncoder)


def _sha256(data):
    return hashlib.sha256(data).digest()


def encode(prefix: str, data) -> str:
    """encode data using the default encoding/decoding algorithm and prepending the prefix with a prefix, ex: ak_encoded_data, th_encoded_data,..."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    if prefix in identifiers.IDENTIFIERS_B64:
        return f"{prefix}_{_base64_encode(data)}"
    return f"{prefix}_{_base58_encode(data)}"


def decode(data):
    """
    Decode data using the default encoding/decoding algorithm
    :param data: a encoded and prefixed string (ex tx_..., sg_..., ak_....)
    :return: the raw bytes
    """

    if data is None or len(data.strip()) < 3 or data[2] != '_':
        raise ValueError('Invalid hash')
    if data[0:2] in identifiers.IDENTIFIERS_B64:
        return _base64_decode(data[3:])
    return _base58_decode(data[3:])


def encode_rlp(prefix, data):
    """
    Encode a list in rlp format
    :param prefix: the prefix to use in the encoded string
    :param data: the array that has to be encoded in rlp
    """
    if not isinstance(data, list):
        raise ValueError("data to be encoded to rlp must be an array")
    payload = rlp.encode(data)
    return encode(prefix, payload)


def decode_rlp(data):
    """
    Decode an rlp/b2b message to a list
    :param data: the encoded string to decode
    """
    rlp_enc = decode(data)
    return rlp.decode(rlp_enc)


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


def _int(val: int) -> bytes:
    """
    Encode and int to a big endian byte array
    """
    if val == 0:
        return val.to_bytes(1, byteorder='big')
    return val.to_bytes((val.bit_length() + 7) // 8, byteorder='big')


def _binary(val):
    """
    Encode a value to bytes.
    If the value is an int it will be encoded as bytes big endian
    Raises ValueError if the input is not an int or string
    """
    if isinstance(val, int) or isinstance(val, float):
        s = int(math.ceil(val.bit_length() / 8))
        return val.to_bytes(s, 'big')
    if isinstance(val, str):
        return val.encode("utf-8")
    if isinstance(val, bytes):
        return val
    raise ValueError("Byte serialization not supported")


def _id(id_tag, hash_id):
    """Utility function to create and _id type"""
    return _int(id_tag) + decode(hash_id)


def contract_id(owner_id, nonce):
    """
    Compute the contract id of a contract
    :param owner_id: the account creating the conctract
    :param nonce: the nonce of the contract creation transaction
    """
    return hash_encode("ct", decode(owner_id) + _int(nonce))


def oracle_id(account_id):
    """
    Compute the oracle id of a oracle registration
    :parm account_id: the account registering the oracle
    """
    return f"ok_{account_id[3:]}"


def oracle_query_id(sender_id, nonce, oracle_id):
    """
    Compute the query id for a sender and an oracle
    :param sender_id: the account making the query
    :param nonce: the nonce of the query transaction
    :param oracle_id: the oracle id
    """
    def _int32(val):
        return val.to_bytes(32, byteorder='big')
    return hash_encode("oq", decode(sender_id) + _int32(nonce) + decode(oracle_id))


def randint(upper_bound=2**64):
    return secrets.randbelow(upper_bound)


def randbytes(size=32):
    return secrets.token_bytes(size)
