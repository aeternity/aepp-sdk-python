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
    return base58.b58encode_check(data).decode("ascii")


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
    if len(raw) < 4:
        raise ValueError("Invalid input for base64 decode check")
    # test checksum
    data, check = raw[:-4], raw[-4:]
    if check != _checksum(data):
        raise ValueError("Checksum mismatch when decoding base64 hash")
    return data


def _blake2b_digest(data):
    """create a blake2b 32 bit raw encoded digest"""
    return blake2b(data=data, digest_size=32, encoder=RawEncoder)


def _sha256(data):
    return hashlib.sha256(data).digest()


def encode(prefix: str, data) -> str:
    """
    Encode data using the default encoding/decoding algorithm and prepending the prefix with a prefix, ex: ak_encoded_data, th_encoded_data,...

    Args:
        prefix(str): the prefix for the encoded string (see identifiers.IDENTIFIERS_B58 and IDENTIFIERS_B64)
        data(str|bytes): the data to encode
    Returns:
        The encoded string using the correct encoding based on the prefix
    Raises:
        ValueError if the prefix is not recognized

    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    if prefix in identifiers.IDENTIFIERS_B64:
        return f"{prefix}_{_base64_encode(data)}"
    elif prefix in identifiers.IDENTIFIERS_B58:
        return f"{prefix}_{_base58_encode(data)}"
    else:
        raise ValueError(f"Unknown prefix {prefix}")


def decode(data: str) -> bytes:
    """
    Decode data using the default encoding/decoding algorithm.

    Args:
        data(str): the string data to decode
    Returns:
        the bytes of the decode data
    Raises:
        ValueError: if the data cannot be recognized or the prefix is unknown
    """
    if data is None or len(data.strip()) <= 3 or data[2] != '_':
        raise ValueError('Invalid input string')
    if data[0:2] in identifiers.IDENTIFIERS_B64:
        return _base64_decode(data[3:])
    if data[0:2] in identifiers.IDENTIFIERS_B58:
        return _base58_decode(data[3:])
    raise ValueError(f"Unknown prefix {data[0:2]}")


def encode_rlp(prefix: str, data: list) -> str:
    """
    Encode input data into rlp + the encoding defined for the prefix

    Args:
        prefix(str): the prefix to use when encoding the rlp to string
        data(list): a list of value to be encoded in rlp
    Returns:
        the string representation (based on prefix) of the rlp encoded message
    Raises:
        TypeError: if the data is not a list
    """
    if not isinstance(data, list):
        raise TypeError("data to be encoded to rlp must be a list")
    payload = rlp.encode(data)
    return encode(prefix, payload)


def decode_rlp(data: str) -> list:
    """
    Decode an rlp/b2b message to a list
    Args:
        the encoded prefixed sting
    Returns:
        the raw data contained in the rlp message
    """
    rlp_enc = decode(data)
    return rlp.decode(rlp_enc)


def hash(data: bytes) -> bytes:
    """
    Compute the hash of the input data using the default algorithm

    Args:
        data(bytes): the data to hash
    Returns:
        the hash of the input data
    """
    return _blake2b_digest(data)


def hash_encode(prefix: str, data: bytes) -> str:
    """
    Compute the hash of the input data and encode the
    result with the encoding mapped for the prefix

    Args:
        prefix(str): the prefix for the data
        data(bytes): the bytes for the input data
    Returns:
        a string composed by the prefix and the encoded hash

    """
    return encode(prefix, hash(data))


def commitment_id(domain: str, salt: int = None) -> tuple:
    """
    Compute the commitment id used in AENS pre-claim transactions

    Args:
        domain(str): the domain for which the commitment_id has to be generated
        salt(int): the salt to use, if not provided it is randomly generated
    Returns:
        a tuple containing the commitment_id and the salt used to generate the commitment_id
    """
    name_salt = randint() if salt is None else salt
    commitment_id = hash_encode(identifiers.COMMITMENT_ID, domain.lower().encode('utf8') + _int(name_salt, 32))
    return commitment_id, name_salt


def _int(val: int, byte_length: int = None) -> bytes:
    """
    Encode and int to a big endian byte array
    :param val: the value to encode
    :param byte_length: number of bytes that should be used to encoded the number, by default is the minimum
    """
    if val < 0:
        raise ValueError(f"Unsupported negative value {val}")
    if val == 0:
        size = 1 if byte_length is None else byte_length
        return val.to_bytes(size, byteorder='big')
    size = (val.bit_length() + 7) // 8 if byte_length is None else byte_length
    return val.to_bytes(size, byteorder='big')


def _int_decode(data: bytes) -> int:
    """
    Interpret a byte array to an integer (big endian)
    """
    if len(data) == 0:
        return 0
    return int.from_bytes(data, "big")


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
        try:
            return decode(val)
        except Exception:
            return val.encode("utf-8")
    if isinstance(val, bytes):
        return val
    raise TypeError("Byte serialization not supported")


def _binary_decode(data, data_type=None):
    """
    Decodes a bite array to the selected datatype or to hex if no data_type is provided
    """
    if data_type == int:
        return _int_decode(data)
    if data_type == str:
        return data.decode("utf-8")
    return data.hex()


def _id(id_str):
    """
    Utility function to create an _id type
    """
    # if not utils.is_valid_hash(id_str):
    #     raise ValueError(f"Unrecognized entity {id_str}")
    id_tag = identifiers.ID_PREFIX_TO_TAG.get(id_str[0:2])
    if id_tag is None:
        raise ValueError(f"Unrecognized prefix {id_str[0:2]}")
    return _int(id_tag) + decode(id_str)


def _id_decode(data):
    """
    Decode and id object to it's API representation
    """
    id_tag = _int_decode(data[0:1])
    prefix = identifiers.ID_TAG_TO_PREFIX.get(id_tag)
    if prefix is None:
        raise ValueError(f"Unrecognized id tag {id_tag}")
    return encode(prefix, data[1:])


def name_id(name: str) -> str:
    """
    Encode a domain name

    Args:
        name(str): the domain name to encode
    Returns:
        the encoded and prefixed name hash
    """
    return encode(identifiers.NAME_ID, hash(name.lower().encode('utf8')))


def contract_id(owner_id: str, nonce: int) -> str:
    """
    Compute the contract id of a contract

    Args:
        owner_id(str): the account creating the contract
        nonce(int): the nonce of the contract creation transaction
    Returns:
        the computed contract_id
    """
    return hash_encode(identifiers.CONTRACT_ID, decode(owner_id) + _int(nonce))


def oracle_id(account_id: str) -> str:
    """
    Compute the oracle id of a oracle registration

    Args:
        account_id(str): the account registering the oracle
    Returns:
        the computed oracle_id
    """
    return f"{identifiers.ORACLE_ID}_{account_id[3:]}"


def oracle_query_id(sender_id: str, nonce: int, oracle_id: str) -> str:
    """
    Compute the query id for a sender and an oracle

    Args:
        sender_id(str): the account making the query
        nonce(int): the nonce of the query transaction
        oracle_id(str): the oracle id
    Returns:
        the computed oracle_query_id
    """
    return hash_encode(identifiers.ORACLE_QUERY_ID, decode(sender_id) + _int(nonce, byte_length=32) + decode(oracle_id))


def randint(upper_bound: int = 2**64):
    """
    Generate a cryptographically secure random int between 0 and `upper_bound`
    It uses the nacl library to do so

    Args:
        upper_bound(int): the upper bound of the generated number (default 2**64)
    Returns:
        a random number
    """
    return secrets.randbelow(upper_bound)


def randbytes(size: int = 32) -> bytes:
    """
    Generate a cryptographically secure random byte sequence of the requested size
    It uses the nacl library to do so.

    Args:
        size(int): the size of the generated byte sequence (default 32)
    Returns:
        a random byte sequence
    """
    return secrets.token_bytes(size)
