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


PUBLIC_KEY = os.environ.get('WALLET_PUB')
PRIVATE_KEY = os.environ.get('WALLET_PRIV')
NODE_URL = os.environ.get('TEST_URL')
NODE_URL_DEBUG = os.environ.get('TEST_DEBUG_URL')
EPOCH_VERSION = '0.24.0'
# set the key folder as environment variables
genesis = Account.from_public_private_key_strings(PUBLIC_KEY, PRIVATE_KEY)
# default values for tests
TEST_FEE = 1
TEST_TTL = 50


Config.set_defaults(Config(
    external_url=NODE_URL,
    internal_url=NODE_URL_DEBUG
))

# Instantiate the epoch client for the tests
EPOCH_CLI = epoch.EpochClient(blocking_mode=True, debug=True)
# create a new account and fill it with some money
ACCOUNT = Account.generate()
EPOCH_CLI.spend(genesis, ACCOUNT.get_address(), 100000)
a = EPOCH_CLI.get_account_by_pubkey(pubkey=ACCOUNT.get_address())
print(f"Test account is {ACCOUNT.get_address()} with balance {a.balance}")


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
    return rand_str + '.aet'
