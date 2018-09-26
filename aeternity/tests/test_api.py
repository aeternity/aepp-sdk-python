from aeternity.tests import PUBLIC_KEY, EPOCH_VERSION, KEYPAIR
from aeternity.epoch import EpochClient
from aeternity.signing import KeyPair

# from aeternity.exceptions import TransactionNotFoundException


def test_api_get_account():
    client = EpochClient()
    account = client.get_account_by_pubkey(pubkey=PUBLIC_KEY)
    assert account.balance > 0


def test_api_get_version():
    client = EpochClient()
    assert client.get_version() == EPOCH_VERSION


def test_api_get_status():
    client = EpochClient()
    status = client.get_status()
    assert status.node_version == EPOCH_VERSION


def test_api_get_top_block():
    client = EpochClient()
    block = client.get_top_block()
    # assert type(block) == BlockWithTx
    assert block.height > 0


def test_api_get_block_by_height():
    client = EpochClient()
    height = client.get_current_key_block_height()

    block = client.get_key_block_by_height(height=height)
    # assert type(block) == BlockWithTx
    assert block.height > 0


def test_api_get_block_by_hash():
    client = EpochClient()

    has_kb, has_mb = False, False
    while not has_kb or not has_mb:
        # the latest block could be both micro or key block
        latest_block = client.get_top_block()
        has_mb = latest_block.hash.startswith("mh_") or has_mb  # check if is a microblock
        has_kb = latest_block.hash.startswith("kh_") or has_kb  # check if is a keyblock
        print(has_kb, has_mb, latest_block.hash)
        # create a transaction so the top block is going to be an micro block
        if not has_mb:
            account = KeyPair.generate().get_address()
            client.spend(KEYPAIR, account, 100)
        # wait for the next block
        # client.wait_for_next_block()
        block = client.get_block_by_hash(hash=latest_block.hash)
        # assert block.hash == latest_block.hash
        assert block.height == latest_block.height


def test_api_get_genesis_block():
    client = EpochClient()
    node_status = client.get_status()
    genesis_block = client.get_key_block_by_hash(hash=node_status.genesis_key_block_hash)
    zero_height_block = client.get_key_block_by_height(height=0)  # these should be equivalent
    # assert type(genesis_block) == BlockWithTx
    # assert type(zero_height_block) == BlockWithTx
    assert genesis_block.height == genesis_block.height == 0
    # TODO: The following check should not fail. I feel that's a problem with
    # TODO: the current state of the api  --devsnd
    assert genesis_block.hash == zero_height_block.hash


def test_api_get_generation_transaction_count_by_hash():
    client = EpochClient()
    # get the latest block
    block_hash = client.get_current_key_block_hash()
    print(block_hash)
    assert block_hash is not None
    # get the transaction count that should be a number >= 0
    generation = client.get_generation_by_hash(hash=block_hash)
    print(generation)
    assert len(generation.micro_blocks) >= 0
