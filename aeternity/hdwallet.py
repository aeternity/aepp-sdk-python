import hmac
import hashlib
from nacl.signing import SigningKey
from mnemonic import Mnemonic
from aeternity.signing import Account

HARDENED_OFFSET = 0x800001c9
AETERNITY_DERIVATION_PATH = "m/44'/457'/0'"
MNEMONIC = Mnemonic(language="english")


def generate_mnemonic():
    """
    Generate mnemonic
    """
    return MNEMONIC.generate()


def generate_wallet(mnemonic=None):
    """
    Generate Account/Wallet
    """
    if mnemonic is None:
        mnemonic = generate_mnemonic()
    if not MNEMONIC.check(mnemonic):
        raise ValueError("Invalid Mnemonic")
    keys = _master_key_from_mnemonic(mnemonic)
    return mnemonic, _get_account(keys["secret_key"])


def _get_account(secret_key):
    """
    Generate Account from secret key

    Args:
        secret_key(bytes): secret key in bytes
    Returns:
        Account instance with generated signing key and verifying key
    """
    sign_key = SigningKey(secret_key)
    return Account(sign_key, sign_key.verify_key)


def _master_key_from_mnemonic(mnemonic):
    return _master_key_from_seed(Mnemonic.to_seed(mnemonic))


def _master_key_from_seed(seed):
    """
    Generates a master key from a provided seed.

    Args:
        seed (str or bytes): a string of bytes or a hex string
    Returns:
        dict containing 'secret_key' and 'chain_code'
    """
    seed = bytes.fromhex(seed) if type(seed) is str else seed
    I_hmac = hmac.new(b'ed25519 seed', seed, hashlib.sha512).digest()
    return {"secret_key": I_hmac[:32], "chain_code": I_hmac[32:]}


def _parse_path(path):
    if isinstance(path, str):
        p = path.rstrip("/").split("/")
    elif isinstance(path, bytes):
        p = path.decode('utf-8').rstrip("/").split("/")
    else:
        p = list(path)

    return p


def _derive_child(parent_key, i):
    if i & HARDENED_OFFSET:
        hmac_data = b'\x00' + parent_key["secret_key"] + i.to_bytes(length=4, byteorder='big')
    I_hmac = hmac.new(parent_key["chain_code"], hmac_data, hashlib.sha512).digest()
    return {"secret_key": I_hmac[:32], "chain_code": I_hmac[32:]}


def _from_path(path, root_key, is_master=True):
    p = _parse_path(path)

    if p[0] == "m":
        if is_master:
            p = p[1:]
        else:
            raise ValueError("root_key must be a master key if 'm' is the first element of the path.")

    keys = [root_key]
    for i in p:
        if isinstance(i, str):
            index = HARDENED_OFFSET + int(i[:-1])
        else:
            index = i
        k = keys[-1]
        keys.append(_derive_child(k, index))

    return keys
