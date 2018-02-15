from aeternity import EpochClient
from aeternity.epoch import AccountBalance, Transaction, CoinbaseTx, Version, EpochInfo, LastBlockInfo, BlockWithTx


client = EpochClient()


def test_get_balance():
    assert client.get_balance() > 0

def test_get_transactions():
    trans = client.get_transactions()
    assert len(trans) > 0
    assert type(trans[0]) == Transaction
    assert type(trans[0].tx) == CoinbaseTx

def test_get_all_balances():
    balances = client.get_all_balances()
    assert len(balances) > 0
    assert type(balances[0]) == AccountBalance

def test_get_version():
    version_info = client.get_version()
    assert type(version_info) == Version
    assert version_info.version == '0.6.0'

def test_get_info():
    info = EpochClient().get_info()
    assert type(info) == EpochInfo
    assert type(info.last_30_blocks_time[0]) == LastBlockInfo
    assert info.last_30_blocks_time[0].time_delta_to_parent > 0

def test_get_latest_block():
    block = client.get_latest_block()
    assert type(block) == BlockWithTx
    assert block.height > 0

def test_get_block_by_heigt():
    height = client.get_height()
    block = client.get_block_by_height(height)
    assert type(block) == BlockWithTx
    assert block.height > 0

def test_get_block_by_hash():
    latest_block = client.get_latest_block()
    block = client.get_block_by_hash(latest_block.hash)
    assert type(block) == BlockWithTx
    # TODO: The following check should not fail. I feel that's a problem with
    # TODO: the current state of the api  --devsnd
    # assert block.hash == latest_block.hash
    assert block.height == latest_block.height

def test_get_genesis_block():
    genesis_block = client.get_genesis_block()
    zero_height_block = client.get_block_by_height(0)  # these should be equivalent
    assert type(genesis_block) == BlockWithTx
    assert type(zero_height_block) == BlockWithTx
    assert genesis_block.height == 0
    assert zero_height_block.height == 0
    # TODO: The following check should not fail. I feel that's a problem with
    # TODO: the current state of the api  --devsnd
    # assert genesis_block.hash == zero_height_block.hash

def test_get_pending_block():
    block = client.get_pending_block()
    assert type(block) == BlockWithTx

def test_get_block_transaction_count_by_hash():
    block = client.get_latest_block()
    assert block.hash is not None
    transaction_count = client.get_block_transaction_count_by_hash(block.hash)
    print(transaction_count)
    assert transaction_count > 0

def test_get_block_transaction_count_by_height():
    previous_height = client.get_height() - 1
    transaction_count = client.get_block_transaction_count_by_height(previous_height)
    print(transaction_count)
    assert transaction_count > 0

def test_get_transaction_from_block_height():
    latest_block = client.get_latest_block()
    print(latest_block)
    transaction = client.get_transaction_from_block_height(latest_block.height, 0)
    print(transaction)
    assert False

def test_get_transactions_in_block_range():
    height = client.get_height()
    result = client.get_transactions_in_block_range(height-5, height)
    assert len(result) > 1
    assert type(result[0]) == Transaction
