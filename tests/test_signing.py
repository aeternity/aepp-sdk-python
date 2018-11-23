from pytest import raises
from tests import ACCOUNT, EPOCH_CLI, tempdir, TEST_FEE, TEST_TTL
from aeternity.signing import Account
from aeternity.utils import is_valid_hash
import os


def test_signing_create_transaction_signature():
    # generate a new account
    new_account = Account.generate()
    receiver_address = new_account.get_address()
    # create a spend transaction
    nonce, ttl = EPOCH_CLI._get_nonce_ttl(ACCOUNT.get_address(), TEST_TTL)
    tx = EPOCH_CLI.tx_builder.tx_spend(ACCOUNT.get_address(), receiver_address, 321, "test test ", TEST_FEE, ttl, nonce)
    tx_signed, signature, tx_hash = EPOCH_CLI.sign_transaction(ACCOUNT, tx)
    # this call will fail if the hashes of the transaction do not match
    EPOCH_CLI.broadcast_transaction(tx_signed)
    # make sure this works for very short block times
    spend_tx = EPOCH_CLI.get_transaction_by_hash(hash=tx_hash)
    assert spend_tx.signatures[0] == signature


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


def test_signing_keystore_load():

    a = Account.from_keystore(os.path.join(os.path.dirname(os.path.realpath(__file__)), "testdata", "keystore.json"), "aeternity")
    assert a.get_address() == "ak_2hSFmdK98bhUw4ar7MUdTRzNQuMJfBFQYxdhN9kaiopDGqj3Cr"


def test_signing_keystore_save_load():
    with tempdir() as tmp_path:
        filename = ACCOUNT.save_to_keystore(tmp_path, "whatever")
        path = os.path.join(tmp_path, filename)
        print(f"\nAccount keystore is {path}")
        # now load again the same
        a = Account.from_keystore(path, "whatever")
        assert a.get_address() == ACCOUNT.get_address()
    with tempdir() as tmp_path:
        filename = "account_ks"
        filename = ACCOUNT.save_to_keystore(tmp_path, "whatever", filename=filename)
        path = os.path.join(tmp_path, filename)
        print(f"\nAccount keystore is {path}")
        # now load again the same
        a = Account.from_keystore(path, "whatever")
        assert a.get_address() == ACCOUNT.get_address()


def test_signing_keystore_save_load_wrong_pwd():
    with tempdir() as tmp_path:
        filename = ACCOUNT.save_to_keystore(tmp_path, "whatever")
        path = os.path.join(tmp_path, filename)
        print(f"\nAccount keystore is {path}")
        # now load again the same
        with raises(ValueError):
            a = Account.from_keystore(path, "nononon")
            assert a.get_address() == ACCOUNT.get_address()
