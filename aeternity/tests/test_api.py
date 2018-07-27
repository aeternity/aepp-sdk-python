from aeternity.tests import PUBLIC_KEY, EPOCH_VERSION
from aeternity.epoch import EpochClient
import pytest

# from aeternity.exceptions import TransactionNotFoundException


def test_api_get_balance():
    client = EpochClient()
    assert client.get_balance(account_pubkey=PUBLIC_KEY) > 0


def test_api_get_version():
    client = EpochClient()
    assert client.get_version() == EPOCH_VERSION


@pytest.mark.skip("it is not a published method")
def test_api_get_info():
    client = EpochClient()
    info = client.get_info()
    assert info.last_30_blocks_time[0].time_delta_to_parent > 0


def test_api_get_latest_block():
    client = EpochClient()
    block = client.get_latest_block()
    # assert type(block) == BlockWithTx
    assert block.height > 0


def test_api_get_block_by_heigt():
    client = EpochClient()
    height = client.get_height()
    block = client.get_key_block_by_height(height)
    # assert type(block) == BlockWithTx
    assert block.height > 0


def test_api_get_block_by_hash():
    client = EpochClient()
    latest_block = client.get_latest_block()
    block = client.get_block_by_hash(latest_block.hash)
    # TODO: The following check should not fail. I feel that's a problem with
    # TODO: the current state of the api  --devsnd
    # assert block.hash == latest_block.hash
    assert block.height == latest_block.height


def test_api_get_genesis_block():
    client = EpochClient()
    genesis_block = client.get_genesis_block()
    zero_height_block = client.get_key_block_by_height(0)  # these should be equivalent
    # assert type(genesis_block) == BlockWithTx
    # assert type(zero_height_block) == BlockWithTx
    assert genesis_block.height == 0
    assert zero_height_block.height == 0
    # TODO: The following check should not fail. I feel that's a problem with
    # TODO: the current state of the api  --devsnd
    # assert genesis_block.hash == zero_height_block.hash


def test_api_get_pending_block():
    # block = client.get_pending_block()
    # assert type(block) == BlockWithTx
    pass


def test_api_get_block_transaction_count_by_hash():
    client = EpochClient()
    # get the latest block
    block = client.get_latest_block()
    print(block)
    assert block.hash is not None
    # get the transaction count that should be a number >= 0
    txs_count = client.get_block_transaction_count_by_hash(block.hash)
    print(txs_count)
    assert txs_count.count >= 0


def test_api_get_block_transaction_count_by_height():
    client = EpochClient()
    previous_height = client.get_height() - 1
    transaction_count = client.get_block_transaction_count_by_height(previous_height)
    print(transaction_count.count)
    assert transaction_count.count >= 0
