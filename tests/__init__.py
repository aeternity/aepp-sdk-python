import logging
import os
from aeternity.config import Config
from aeternity.signing import Account
from aeternity import epoch
# for tempdir
import shutil
import tempfile
from contextlib import contextmanager
import random
import string

logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("aeternity").setLevel(logging.DEBUG)
logging.root.setLevel(logging.DEBUG)


PUBLIC_KEY = os.environ.get('WALLET_PUB')
PRIVATE_KEY = os.environ.get('WALLET_PRIV')
NODE_URL = os.environ.get('TEST_URL')
NODE_URL_DEBUG = os.environ.get('TEST_DEBUG_URL')
NETWORK_ID = os.environ.get('TEST_NETWORK_ID')
# set the key folder as environment variables
genesis = Account.from_public_private_key_strings(PUBLIC_KEY, PRIVATE_KEY)
# default values for tests
TEST_FEE = 20000
TEST_TTL = 50


Config.set_defaults(Config(
    external_url=NODE_URL,
    internal_url=NODE_URL_DEBUG,
    network_id=NETWORK_ID
))

# Instantiate the epoch client for the tests
EPOCH_CLI = epoch.EpochClient(blocking_mode=True, debug=True, native=False)
# create a new account and fill it with some money
ACCOUNT = Account.generate()
EPOCH_CLI.spend(genesis, ACCOUNT.get_address(), 1000000000)
a = EPOCH_CLI.get_account_by_pubkey(pubkey=ACCOUNT.get_address())
print(f"Test account is {ACCOUNT.get_address()} with balance {a.balance}")

ACCOUNT_1 = Account.generate()  # required for oracles
EPOCH_CLI.spend(genesis, ACCOUNT_1.get_address(), 1000000000)
a = EPOCH_CLI.get_account_by_pubkey(pubkey=ACCOUNT_1.get_address())
print(f"Test account (1) is {ACCOUNT_1.get_address()} with balance {a.balance}")


@contextmanager
def tempdir():
    # contextmanager to generate and delete a temporary directory
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def random_domain(length=10):
    rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return f"{rand_str}.test"
