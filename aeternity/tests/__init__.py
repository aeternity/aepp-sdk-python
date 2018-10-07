import logging
import os
from aeternity.config import Config
from aeternity.signing import Account
from aeternity import epoch
# for tempdir
import shutil
import tempfile
from contextlib import contextmanager

logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("aeternity").setLevel(logging.DEBUG)


PUBLIC_KEY = os.environ.get('WALLET_PUB')
PRIVATE_KEY = os.environ.get('WALLET_PRIV')
NODE_URL = os.environ.get('TEST_URL')
NODE_URL_INTERNAL = os.environ.get('TEST_INTERNAL_URL')
EPOCH_VERSION = '0.22.0'
# set the key folder as environment variables
genesis = Account.from_public_private_key_strings(PUBLIC_KEY, PRIVATE_KEY)
# default values for tests
TEST_FEE = 1
TEST_TTL = 50


Config.set_defaults(Config(
    external_url=NODE_URL,
    internal_url=NODE_URL_INTERNAL
))

# Instantiate the epoch client for the tests
EPOCH_CLI = epoch.EpochClient(blocking_mode=True, debug=True)
# create a new account and fill it with some money
KEYPAIR = Account.generate()
EPOCH_CLI.spend(genesis, KEYPAIR.get_address(), 100000)
print(f"Test account is {KEYPAIR.get_address()} with balance {100000}")


@contextmanager
def tempdir():
    # contextmanager to generate and delete a temporary directory
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)
