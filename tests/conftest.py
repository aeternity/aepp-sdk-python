import pytest
import os
import namedtupled
import shutil
import tempfile
import random
import string
from aeternity.signing import Account
from aeternity.node import NodeClient, Config
from aeternity.contract import CompilerClient


PUBLIC_KEY = os.environ.get('WALLET_PUB')
PRIVATE_KEY = os.environ.get('WALLET_PRIV')
NODE_URL = os.environ.get('TEST_URL', 'http://localhost:3013')
NODE_URL_DEBUG = os.environ.get('TEST_DEBUG_URL', 'http://localhost:3113')
NETWORK_ID = os.environ.get('TEST_NETWORK_ID', 'ae_devnet')
COMPILER_URL = os.environ.get("COMPILER_URL", 'http://localhost:3080')


@pytest.fixture
def tempdir(scope="module"):
    # contextmanager to generate and delete a temporary directory
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def random_domain(length=10, tld='aet'):
    rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return f"{rand_str}.{tld}"


@pytest.fixture
def client_fixture(scope="module"):
    # Instantiate the node client for the tests
    NODE_CLI = NodeClient(Config(
        external_url=NODE_URL,
        internal_url=NODE_URL_DEBUG,
        # network_id=NETWORK_ID,
        blocking_mode=True,
        debug=True,
    ))
    return namedtupled.map({"NODE_CLI": NODE_CLI}, _nt_name="TestData")


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

    NODE_CLI.spend(genesis, ACCOUNT.get_address(), 5000000000000000000000) # 5000AE
    a = NODE_CLI.get_account_by_pubkey(pubkey=ACCOUNT.get_address())
    print(f"Test account is {ACCOUNT.get_address()} with balance {a.balance}")

    NODE_CLI.spend(genesis, ACCOUNT_1.get_address(), 5000000000000000000000) # 5000AE
    a = NODE_CLI.get_account_by_pubkey(pubkey=ACCOUNT_1.get_address())
    print(f"Test account (1) is {ACCOUNT_1.get_address()} with balance {a.balance}")

    return namedtupled.map({"NODE_CLI": NODE_CLI, "ALICE": ACCOUNT, "BOB": ACCOUNT_1}, _nt_name="TestData")


@pytest.fixture
def compiler_fixture(scope="module"):
    # Instantiate the node client for the tests
    compiler = CompilerClient(COMPILER_URL)
    return namedtupled.map({"COMPILER": compiler}, _nt_name="TestData")

@pytest.fixture
def testdata_fixture(scope="module"):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "testdata")
