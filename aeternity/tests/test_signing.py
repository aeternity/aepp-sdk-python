
from aeternity.tests import PUBLIC_KEY, PRIVATE_KEY
from aeternity.epoch import EpochClient
from aeternity.signing import KeyPair, is_valid_hash


def test_signing_create_transaction():
    client = EpochClient()
    # generate a new keypair
    new_keypair = KeyPair.generate()
    receiver_address = new_keypair.get_address()
    # get the test keypair
    keypair = KeyPair.from_public_private_key_strings(PUBLIC_KEY, PRIVATE_KEY)
    # create a spend transaction
    transaction = client.create_spend_transaction(PUBLIC_KEY, receiver_address, 321, payload="test payload")
    signed_transaction, b58signature = keypair.sign_transaction(transaction)
    # post the transaction
    result = client.send_signed_transaction(signed_transaction)
    assert result is not None
    assert result.tx_hash is not None
    print(result)

    # make sure this works for very short block times
    client.wait_for_next_block(5)
    spend_tx = client.get_transaction_by_hash(hash=result.tx_hash)
    assert spend_tx.signatures[0] == b58signature


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
