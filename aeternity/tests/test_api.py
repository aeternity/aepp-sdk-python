from aeternity.tests import PUBLIC_KEY, EPOCH_VERSION, ACCOUNT, EPOCH_CLI
from aeternity.signing import Account
from aeternity import openapi

# from aeternity.exceptions import TransactionNotFoundException


def test_api_get_account():

    account = EPOCH_CLI.get_account_by_pubkey(pubkey=PUBLIC_KEY)
    assert account.balance > 0


def test_api_get_version():
    assert EPOCH_CLI.get_version() == EPOCH_VERSION


def test_api_get_status():
    status = EPOCH_CLI.get_status()
    assert status.node_version == EPOCH_VERSION


def test_api_get_top_block():
    block = EPOCH_CLI.get_top_block()
    # assert type(block) == BlockWithTx
    assert block.height > 0


def test_api_get_block_by_height():
    height = EPOCH_CLI.get_current_key_block_height()

    block = EPOCH_CLI.get_key_block_by_height(height=height)
    # assert type(block) == BlockWithTx
    assert block.height > 0


def test_api_get_block_by_hash():

    has_kb, has_mb = False, False
    while not has_kb or not has_mb:
        # the latest block could be both micro or key block
        latest_block = EPOCH_CLI.get_top_block()
        has_mb = latest_block.hash.startswith("mh_") or has_mb  # check if is a microblock
        has_kb = latest_block.hash.startswith("kh_") or has_kb  # check if is a keyblock
        print(has_kb, has_mb, latest_block.hash)
        # create a transaction so the top block is going to be an micro block
        if not has_mb:
            account = Account.generate().get_address()
            EPOCH_CLI.spend(ACCOUNT, account, 100)
        # wait for the next block
        # client.wait_for_next_block()
        block = EPOCH_CLI.get_block_by_hash(hash=latest_block.hash)
        # assert block.hash == latest_block.hash
        assert block.height == latest_block.height


def test_api_get_genesis_block():
    node_status = EPOCH_CLI.get_status()
    genesis_block = EPOCH_CLI.get_key_block_by_hash(hash=node_status.genesis_key_block_hash)
    zero_height_block = EPOCH_CLI.get_key_block_by_height(height=0)  # these should be equivalent
    # assert type(genesis_block) == BlockWithTx
    # assert type(zero_height_block) == BlockWithTx
    assert genesis_block.height == genesis_block.height == 0
    # TODO: The following check should not fail. I feel that's a problem with
    # TODO: the current state of the api  --devsnd
    assert genesis_block.hash == zero_height_block.hash


def test_api_get_generation_transaction_count_by_hash():
    # get the latest block
    block_hash = EPOCH_CLI.get_current_key_block_hash()
    print(block_hash)
    assert block_hash is not None
    # get the transaction count that should be a number >= 0
    generation = EPOCH_CLI.get_generation_by_hash(hash=block_hash)
    print(generation)
    assert len(generation.micro_blocks) >= 0


def test_api_get_transaction_by_hash_not_found():
    tx_hash = 'th_LUKGEWyZSwyND7vcQwZwLgUXi23WJLQb9jKgJTr1it9QFViMC'
    try:
        EPOCH_CLI.get_transaction_by_hash(hash=tx_hash)
        assert False
    except openapi.OpenAPIClientException as e:
        assert e.code == 404


def test_api_get_transaction_by_hash_bad_request():
    tx_hash = 'th_LUKG'
    try:
        EPOCH_CLI.get_transaction_by_hash(hash=tx_hash)
        assert False
    except openapi.OpenAPIClientException as e:
        assert e.code == 400
