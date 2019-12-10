import pytest
import os
import shutil
import tempfile
import random
import string
from munch import Munch
from aeternity.signing import Account
from aeternity.node import NodeClient, Config
from aeternity.compiler import CompilerClient


PUBLIC_KEY = os.environ.get('WALLET_PUB')
PRIVATE_KEY = os.environ.get('WALLET_PRIV')
NODE_URL = os.environ.get('TEST_URL', 'http://localhost:3013')
NODE_URL_DEBUG = os.environ.get('TEST_DEBUG_URL', 'http://localhost:3113')
NETWORK_ID = os.environ.get('TEST_NETWORK_ID', 'ae_devnet')
COMPILER_URL = os.environ.get("COMPILER_URL", 'http://localhost:3080')
FORCE_COMPATIBILITY = os.environ.get("FORCE_COMPATIBILITY", False)


@pytest.fixture
def tempdir(scope="module"):
    # contextmanager to generate and delete a temporary directory
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def random_domain(length=10, tld='chain'):
    rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return f"{rand_str}.{tld}"


@pytest.fixture
def client_fixture(scope="module"):
    # Instantiate the node client for the tests
    fc = True if FORCE_COMPATIBILITY == "true" else False
    NODE_CLI = NodeClient(Config(
        external_url=NODE_URL,
        internal_url=NODE_URL_DEBUG,
        # network_id=NETWORK_ID,
        blocking_mode=True,
        debug=True,
        force_compatibility=fc,
    ))
    return Munch.fromDict({"NODE_CLI": NODE_CLI})


@pytest.fixture
def chain_fixture(scope="module"):

    # create a new account and fill it with some money
    ACCOUNT = Account.generate()
    ACCOUNT_1 = Account.generate()  # used by for oracles
    # set the key folder as environment variables
    genesis = Account.from_private_key_string(PRIVATE_KEY)

    # Instantiate the node client for the tests
    NODE_CLI = NodeClient(Config(
        external_url=NODE_URL,
        internal_url=NODE_URL_DEBUG,
        # network_id=NETWORK_ID,
        blocking_mode=True,
        debug=True,
    ))

    NODE_CLI.spend(genesis, ACCOUNT.get_address(), '5000AE')
    a = NODE_CLI.get_account_by_pubkey(pubkey=ACCOUNT.get_address())
    print(f"Test account is {ACCOUNT.get_address()} with balance {a.balance}")

    NODE_CLI.spend(genesis, ACCOUNT_1.get_address(), '5000AE')
    a = NODE_CLI.get_account_by_pubkey(pubkey=ACCOUNT_1.get_address())
    print(f"Test account (1) is {ACCOUNT_1.get_address()} with balance {a.balance}")

    return Munch.fromDict({"NODE_CLI": NODE_CLI, "ALICE": ACCOUNT, "BOB": ACCOUNT_1})


@pytest.fixture
def compiler_fixture(scope="module"):
    # Instantiate the node client for the tests
    compiler = CompilerClient(COMPILER_URL)
    return Munch.fromDict({"COMPILER": compiler})

@pytest.fixture
def testdata_fixture(scope="module"):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "testdata")
