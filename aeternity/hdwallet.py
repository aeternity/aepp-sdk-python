import hmac
import hashlib
import json
from nacl.signing import SigningKey
from mnemonic import Mnemonic
from aeternity.signing import Account, keystore_seal, keystore_open, save_keystore_to_file, save_keystore_to_folder
from aeternity.identifiers import SECRET_TYPE_BIP39


class HDWallet():

    HARDENED_OFFSET = 0x80000000
    AETERNITY_DERIVATION_PATH = "m/44'/457'/%d'/0'/%d'"
    MNEMONIC = Mnemonic(language="english")

    def __init__(self, mnemonic=None):
        if mnemonic is None:
            mnemonic = self.generate_mnemonic()
        if not self.MNEMONIC.check(mnemonic):
            raise ValueError("Invalid Mnemonic")
        self.mnemonic = mnemonic
        self.master_key = self._master_key_from_mnemonic(mnemonic)
        self.master_account = HDWallet._get_account(self.master_key["secret_key"])
        self.account_index = 0

    @staticmethod
    def generate_mnemonic():
        """
        Generate mnemonic
        """
        return HDWallet.MNEMONIC.generate()

    def derive_child(self, account_index=None, address_index=0):
        """
        Derives the account using the master key
        Args:
            account_index(int): Account index to use for derivation path (optional)
            address_index(int): Address index to use for derivation path (default: 0)
        Returns:
            derivation path and generated account
        """
        if account_index is None:
            account_index = self.account_index
            self.account_index += 1
        derivation_path = self.AETERNITY_DERIVATION_PATH % (account_index, address_index)
        derived_keys = HDWallet._from_path(derivation_path, self.master_key)
        return derivation_path, HDWallet._get_account(derived_keys[-1]["secret_key"])

    def get_master_key(self):
        """
        Returns the master key
        """
        return self.master_key

    def get_master_account(self):
        """
        Returns the account generated using the master_key
        """
        return self.master_account

    def mnemonic_to_keystore(self, password):
        return keystore_seal(self.mnemonic, password, secret_type=SECRET_TYPE_BIP39)

    def save_mnemonic_to_keystore_file(self, path, password):
        """
        Utility method for save_to_keystore
        """
        return save_keystore_to_file(path, self.mnemonic_to_keystore(password))

    def save_mnemonic_to_keystore(self, path, password):
        """
        Save an account in a Keystore/JSON format
        :param path: the folder where to store the keystore file
        :param password: the password for the keystore
        :return: the filename that has been used for the keystore
        """
        return save_keystore_to_folder(path, self.mnemonic_to_keystore(password), self.master_account.get_address())

    @staticmethod
    def from_keystore(path, password=""):
        with open(path) as fp:
            keystore = json.load(fp)
        if keystore.get("crypto", {}).get("secret_type") == SECRET_TYPE_BIP39:
            mnemonic = keystore_open(keystore, password).decode()
            return HDWallet(mnemonic)
        else:
            raise TypeError(f"Invalid keystore. Expected keystore of type {SECRET_TYPE_BIP39}")

    @staticmethod
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

    @staticmethod
    def _master_key_from_mnemonic(mnemonic):
        """
        Generate master key from a given mnemonic
        Args:
            mnemonic (str): a BIP39 compliant mnemonic string
        Returns:
            dict containing 'secret_key' and 'chain_code'
        """
        return HDWallet._master_key_from_seed(Mnemonic.to_seed(mnemonic))

    @staticmethod
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

    @staticmethod
    def _parse_path(path):
        if isinstance(path, str):
            p = path.rstrip("/").split("/")
        elif isinstance(path, bytes):
            p = path.decode('utf-8').rstrip("/").split("/")
        else:
            p = list(path)

        return p

    @staticmethod
    def _derive_child_key(parent_key, i):
        if i & HDWallet.HARDENED_OFFSET:
            hmac_data = b'\x00' + parent_key["secret_key"] + i.to_bytes(length=4, byteorder='big')
        I_hmac = hmac.new(parent_key["chain_code"], hmac_data, hashlib.sha512).digest()
        return {"secret_key": I_hmac[:32], "chain_code": I_hmac[32:]}

    @staticmethod
    def _from_path(path, root_key, is_master=True):
        p = HDWallet._parse_path(path)

        if p[0] == "m":
            if is_master:
                p = p[1:]
            else:
                raise ValueError("root_key must be a master key if 'm' is the first element of the path.")

        keys = [root_key]
        for i in p:
            if isinstance(i, str):
                index = int(i[:-1]) | HDWallet.HARDENED_OFFSET
            else:
                index = i
            k = keys[-1]
            keys.append(HDWallet._derive_child_key(k, index))

        return keys
