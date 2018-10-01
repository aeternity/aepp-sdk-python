
from aeternity.tests import TEST_FEE, TEST_TTL, EPOCH_CLI, KEYPAIR
from aeternity.signing import Account
from aeternity.utils import is_valid_hash
from aeternity.transactions import TxBuilder


def test_signing_create_transaction():
    # generate a new account
    new_account = Account.generate()
    receiver_address = new_account.get_address()
    # create a spend transaction
    txb = TxBuilder(EPOCH_CLI, KEYPAIR)
    tx, sg, tx_hash = txb.tx_spend(receiver_address, 321, "test test ", TEST_FEE, TEST_TTL)
    # this call will fail if the hashes of the transaction do not match
    txb.post_transaction(tx, tx_hash)
    # make sure this works for very short block times
    spend_tx = EPOCH_CLI.get_transaction_by_hash(hash=tx_hash)
    assert spend_tx.signatures[0] == sg


def test_signing_is_valid_hash():
    # input (hash_str, prefix, expected output)
    args = [
        ('ak_me6L5SSXL4NLWv5EkQ7a16xaA145Br7oV4sz9JphZgsTsYwGC', None, True),
        ('ak_me6L5SSXL4NLWv5EkQ7a16xaA145Br7oV4sz9JphZgsTsYwGC', 'ak', True),
        ('ak_me6L5SSXL4NLWv5EkQ7a16xaA145Br7oV4sz9JphZgsTsYwGC', 'bh', False),
        ('ak_me6L5SSXL4NLWv5EkQ7a16xaA145Br7oV4sz9JphZgsTsYwYC', None, False),
        ('ak_me6L5SSXL4NLWv5EkQ7a18xaA145Br7oV4sz9JphZgsTsYwGC', None, False),
        ('bh_vzUC2jVuAfpBC3tMAHhxwxJnTFymckNYeQ5TWZua1pydabqNu', None, True),
        ('th_YqPSTzs73PiKFhFcALYWWu41uNLc6yp63ZC35jzzuJYA9PMui', None, True),
    ]

    for a in args:
        got = is_valid_hash(a[0], a[1])
        expected = a[2]
        assert got == expected
