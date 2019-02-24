import pytest
import os
import namedtupled
import shutil
import tempfile
import random
import string
from aeternity.signing import Account
from aeternity.config import Config
from aeternity.node import NodeClient


PUBLIC_KEY = os.environ.get('WALLET_PUB')
PRIVATE_KEY = os.environ.get('WALLET_PRIV')
NODE_URL = os.environ.get('TEST_URL')
NODE_URL_DEBUG = os.environ.get('TEST_DEBUG_URL')
NETWORK_ID = os.environ.get('TEST_NETWORK_ID')


@pytest.fixture
def tempdir(scope="module"):
    # contextmanager to generate and delete a temporary directory
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)


@pytest.fixture
def random_domain(length=10):
    rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return f"{rand_str}.test"


@pytest.fixture
def account_path(chain_fixture):
    with tempdir() as tmp_path:
        # save the private key on file
        sender_path = os.path.join(tmp_path, 'sender')
        chain_fixture.ACCOUNT.save_to_keystore_file(sender_path, 'aeternity_bc')
        yield sender_path


@pytest.fixture
def chain_fixture(scope="module"):

    # create a new account and fill it with some money
    ACCOUNT = Account.generate()
    ACCOUNT_1 = Account.generate()  # used by for oracles
    # set the key folder as environment variables
    genesis = Account.from_public_private_key_strings(PUBLIC_KEY, PRIVATE_KEY)

    Config.set_defaults(Config(
        external_url=NODE_URL,
        internal_url=NODE_URL_DEBUG,
        network_id=NETWORK_ID
    ))

    # Instantiate the node client for the tests
    NODE_CLI = NodeClient(blocking_mode=True, debug=True, native=False)

    NODE_CLI.spend(genesis, ACCOUNT.get_address(), 2000000000000000000)
    a = NODE_CLI.get_account_by_pubkey(pubkey=ACCOUNT.get_address())
    print(f"Test account is {ACCOUNT.get_address()} with balance {a.balance}")

    NODE_CLI.spend(genesis, ACCOUNT_1.get_address(), 2000000000000000000)
    a = NODE_CLI.get_account_by_pubkey(pubkey=ACCOUNT_1.get_address())
    print(f"Test account (1) is {ACCOUNT_1.get_address()} with balance {a.balance}")

    return namedtupled.map({"NODE_CLI": NODE_CLI, "ACCOUNT": ACCOUNT, "ACCOUNT_1": ACCOUNT_1}, _nt_name="TestData")
