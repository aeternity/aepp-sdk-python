from aeternity.tests import PUBLIC_KEY, EPOCH_VERSION
from aeternity.epoch import EpochClient
import pytest

# from aeternity.exceptions import TransactionNotFoundException


def test_get_balance():
    client = EpochClient()
    assert client.get_balance(account_pubkey=PUBLIC_KEY) > 0


def test_get_transactions():
    client = EpochClient()
    trans = client.get_transactions(account_pubkey=PUBLIC_KEY)
    assert len(trans) > 0
    # assert type(trans[0]) == Transaction
    # all_transaction_types = set(transaction_type_mapping.values())
    # assert type(trans[0].tx) in all_transaction_types


def test_get_version():
    client = EpochClient()
    assert client.get_version() == EPOCH_VERSION


@pytest.mark.skip("it is not a published method")
def test_get_info():
    client = EpochClient()
    info = client.get_info()
    assert info.last_30_blocks_time[0].time_delta_to_parent > 0


def test_get_latest_block():
    client = EpochClient()
    block = client.get_latest_block()
    # assert type(block) == BlockWithTx
    assert block.height > 0


def test_get_block_by_heigt():
    client = EpochClient()
    height = client.get_height()
    block = client.get_block_by_height(height)
    # assert type(block) == BlockWithTx
    assert block.height > 0


def test_get_block_by_hash():
    client = EpochClient()
    latest_block = client.get_latest_block()
    block = client.get_block_by_hash(latest_block.hash)
    # TODO: The following check should not fail. I feel that's a problem with
    # TODO: the current state of the api  --devsnd
    # assert block.hash == latest_block.hash
    assert block.height == latest_block.height


def test_get_genesis_block():
    client = EpochClient()
    genesis_block = client.get_genesis_block()
    zero_height_block = client.get_block_by_height(0)  # these should be equivalent
    # assert type(genesis_block) == BlockWithTx
    # assert type(zero_height_block) == BlockWithTx
    assert genesis_block.height == 0
    assert zero_height_block.height == 0
    # TODO: The following check should not fail. I feel that's a problem with
    # TODO: the current state of the api  --devsnd
    # assert genesis_block.hash == zero_height_block.hash


def test_get_pending_block():
    # block = client.get_pending_block()
    # assert type(block) == BlockWithTx
    pass


def test_get_block_transaction_count_by_hash():
    client = EpochClient()
    # get the latest block
    block = client.get_latest_block()
    print(block)
    assert block.hash is not None
    # get the transaction count that should be a number >= 0
    txs_count = client.get_block_transaction_count_by_hash(block.hash)
    print(txs_count)
    assert txs_count.count >= 0


def test_get_block_transaction_count_by_height():
    client = EpochClient()
    previous_height = client.get_height() - 1
    transaction_count = client.get_block_transaction_count_by_height(previous_height)
    print(transaction_count.count)
    assert transaction_count.count >= 0


def test_get_transaction_from_block_height():
    # latest_block = client.get_latest_block()
    # transaction = client.get_transaction_from_block_height(latest_block.height, 1)
    # assert type(transaction) == Transaction
    pass


def test_get_missing_transaction_from_block_height():
    # latest_block = client.get_latest_block()
    # with raises(TransactionNotFoundException):
    #     transaction = client.get_transaction_from_block_height(latest_block.height, -1)
    #     print(transaction)
    pass


def test_get_transactions_in_block_range():
    client = EpochClient()
    height = client.get_height()
    result = client.get_transactions_in_block_range(height - 5, height)
    assert len(result) > 1
    # assert type(result[0]) == Transaction
