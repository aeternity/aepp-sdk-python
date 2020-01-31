
from aeternity.signing import Account
from aeternity import transactions, exceptions, identifiers as idf, hashing
import pytest
from pytest import raises
import json
from munch import Munch


def _execute_test(test_cases, NODE_CLI):
    for tt in test_cases:
        # get a native transaction
        txbn = transactions.TxBuilder()
        txn = getattr(txbn, tt.get("tx"))(**tt["native"])
        # get a debug transaction
        txbd = transactions.TxBuilder(api=NODE_CLI, native=False)
        txd = getattr(txbd, tt.get("tx"))(**tt["debug"])
        # theys should be the same
        if tt["match"]:
            assert txn == txd
        else:
            assert txn != txd


def test_transaction_fee_calculation():
    sender_id = Account.generate().get_address()
    recipient_id = Account.generate().get_address()
    # account_id, recipient_id, amount, payload, fee, ttl, nonce
    tts = [
        {
            "native": (sender_id, recipient_id, 1000, "", 16740000000000, 0, 1),
            "field_fee_idx": 4,
            "want_err": False
        }, {
            "native": (sender_id, recipient_id, 9845, "another payload", 26740000000000, 500, 1241),
            "field_fee_idx": 4,
            "want_err": False
        }, {
            "native": (sender_id, recipient_id, 9845, "another payload", 26740000000000, 0, 32131),
            "field_fee_idx": 4,
            "want_err": False
        }, {
            "native": (sender_id, recipient_id, 410000, "this is a very long payload that is not good to have ", 96740000000000, 0, 1241),
            "field_fee_idx": 4,
            "want_err": False
        }, {
            "native": (sender_id, recipient_id, 410000, "another payload", 26740000000000, 0, 1241),
            "field_fee_idx": 4,
            "want_err": False
        }, {
            "native": (sender_id, recipient_id, 5000000000000000000, "Faucet TX", 26740000000000, 0, 1241),
            "field_fee_idx": 4,
            "want_err": False  # 16920000000000
        }, {
            "native": (sender_id, recipient_id, 50000000, "", -1, 0, 1241),
            "field_fee_idx": 4,
            "want_err": True
        }, {
            "native": (sender_id, recipient_id, 50000000, "", 321312, 0, 1241),
            "field_fee_idx": 4,
            "want_err": True
        },
    ]

    for tt in tts:
        # get a native transaction
        txbn = transactions.TxBuilder()
        try:
            txbn.tx_spend(tt["native"][0], tt["native"][1], tt["native"][2], tt["native"][3], tt["native"][4], tt["native"][5], tt["native"][6])
        except exceptions.TransactionFeeTooLow:
            assert(tt["want_err"])
        except ValueError:
            assert(tt["want_err"])
        # get a debug transaction

def test_transaction_tx_signer():
    sk = 'ed067bef18b3e2be42822b32e3fa468ceee1c8c2c8744ca15e96855b0db10199af08c7e24c71c39f119f07616621cb86d774c7af07b84e9fd82cc9592c7f7d0a'
    pk = 'ak_2L61wjvTKBKK985sbgn7vryr66K8F4ZwyUVrzYYvro85j5sCeU'
    tx = 'tx_+FAMAaEBrwjH4kxxw58RnwdhZiHLhtd0x68HuE6f2CzJWSx/fQqhAa8Ix+JMccOfEZ8HYWYhy4bXdMevB7hOn9gsyVksf30KZIUukO3QAAABgJoyIic='
    sg = 'sg_Tzrf8pDzK53RVfiTdr3GnM86E4jWoGmA2RR6XaCws4PFfnbUTGQ2adRWc8Y55NpxXBaEYD5b1FP5RzNST1GpBZUVfZrLo'
    network_id = "ae_testnet"
    account = Account.from_secret_key_string(sk)
    with raises(ValueError):
        txs = transactions.TxSigner(None, network_id)
    with raises(ValueError):
        txs = transactions.TxSigner(account, None)

    # parse the transaction
    txo = transactions.TxBuilder().parse_tx_string(tx)
    # verify the signature
    signer = transactions.TxSigner(account, network_id)
    signature = signer.sign_transaction(txo)
    assert f"{signer}" == f"{network_id}:{account.get_address()}"
    assert signature == sg
    # incorrect network_id
    signer = transactions.TxSigner(account, "not_good")
    signature = signer.sign_transaction(txo)
    assert signature != sg


def test_transaction_tx_object_signed():
    sk = 'ed067bef18b3e2be42822b32e3fa468ceee1c8c2c8744ca15e96855b0db10199af08c7e24c71c39f119f07616621cb86d774c7af07b84e9fd82cc9592c7f7d0a'
    pk = 'ak_2L61wjvTKBKK985sbgn7vryr66K8F4ZwyUVrzYYvro85j5sCeU'
    tx = 'tx_+FAMAaEBrwjH4kxxw58RnwdhZiHLhtd0x68HuE6f2CzJWSx/fQqhAa8Ix+JMccOfEZ8HYWYhy4bXdMevB7hOn9gsyVksf30KZIUukO3QAAABgJoyIic='
    sg = 'sg_Tzrf8pDzK53RVfiTdr3GnM86E4jWoGmA2RR6XaCws4PFfnbUTGQ2adRWc8Y55NpxXBaEYD5b1FP5RzNST1GpBZUVfZrLo'
    th = 'th_LL9hH3LvaLYdzm1wXnFeaBkhbNtsqZFCFfWf7oo5rtMMUC3Jk'
    network_id = "ae_testnet"

    txb = transactions.TxBuilder()
    txo = txb.parse_tx_string(tx)
    # create a signed transaction
    txs = txb.tx_signed([sg], txo)
    # verify the hash
    assert txs.hash == th
    assert transactions.TxBuilder.compute_tx_hash(txs.tx) == th
    assert txs.get("signatures")[0] == sg


def test_transaction_tx_object_spend():
    amount=1870600000000000000
    fee=20500000000000
    nonce=316260
    payload="ba_VGltZSBpcyBtb25leSwgbXkgZnJpZW5kcy4gL1lvdXJzIEJlZXBvb2wuLyrtvsY="
    recipient_id="ak_YZeWQYL8UzStPmvPdQREcvrdVTAA6xd3jim3PohRbMX2983hg"
    sender_id="ak_nv5B93FPzRHrGNmMdTDfGdd5xGZvep3MVSpJqzcQmMp59bBCv"
    _type="SpendTx"
    ttl = 0
    version=1
    tag=idf.OBJECT_TAG_SPEND_TRANSACTION
    signatures="sg_RogsZGaYNefpT9hCZwEQNbgHVqWeR8MHD624xUYPjgjQPnK61vAuw7i63kCsYCiaRpbkYgyZEF4i9ipDAB6VS1AhrARwh"
    tx_hash="th_JPyq2xJuxsm8qWdwuySnGde9SU2CTqvqKFikW2jLoTfyMg2BF"
    # meta properties
    meta_min_fee = 17740000000000


    api_spend_tx = {
        "amount":amount,
        "fee":fee,
        "nonce":nonce,
        "payload":payload,
        "recipient_id":recipient_id,
        "sender_id":sender_id,
        "type":_type,
        "version":version
    }

    api_signed_tx = Munch.fromDict({
        "block_height":181115,
        "block_hash":"mh_2essz8vfq4A8UZU98Jpm5VcB3Wt7p5CbQhzBgojjsM4AFq6z2s",
        "hash":tx_hash,
        "signatures":[
            signatures
        ],
        "tx": api_spend_tx
    })


    txbl = transactions.TxBuilder()
    txo_from_py = txbl.tx_spend(sender_id, recipient_id, amount, hashing.decode(payload), fee, ttl, nonce)
    txo_from_api = txbl.parse_node_reply(api_signed_tx).data.tx
    txo_from_str = txbl.parse_tx_string(txo_from_py.tx)

    assert txo_from_py.tx                  == txo_from_str.tx
    assert txo_from_py.tx                  == txo_from_api.tx
    assert txo_from_py.get("recipient_id") == txo_from_api.get("recipient_id") == txo_from_str.get("recipient_id") == recipient_id
    assert txo_from_py.meta("min_fee")     == meta_min_fee
    assert txo_from_api.meta("min_fee")     == meta_min_fee
    assert txo_from_str.meta("min_fee")     == meta_min_fee


