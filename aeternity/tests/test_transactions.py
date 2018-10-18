from aeternity.tests import ACCOUNT, EPOCH_CLI
from aeternity.signing import Account
from aeternity import transactions


def test_transaction_spend():

    recipient_id = Account.generate().get_address()

    tts = [
        {
            "native": (recipient_id, 1000, 1, 100, "payload"),
            "debug": (recipient_id, 1000, 1, 100, "payload"),
            "match": True
        }, {
            "native": (recipient_id, 9845, 1, 500, "another payload"),
            "debug": (recipient_id, 9845, 1, 500, "another payload"),
            "match": True
        }, {
            "native": (recipient_id, 9845, 1, 500, "another payload"),
            "debug": (Account.generate().get_address(), 9845, 1, 500, "another payload"),
            "match": False
        },
    ]

    for tt in tts:
        # get a native transaction
        txbn = transactions.TxBuilder(EPOCH_CLI, ACCOUNT, native=True)
        txn, sn, txhn = txbn.tx_spend(tt["native"][0], tt["native"][1], tt["native"][4], tt["native"][2], tt["native"][3])
        # get a debug transaction
        txbd = transactions.TxBuilder(EPOCH_CLI, ACCOUNT, native=False)
        txd, sd, txhd = txbd.tx_spend(tt["debug"][0], tt["debug"][1], tt["debug"][4], tt["debug"][2], tt["debug"][3])
        # theys should be the same
        if tt["match"]:
            assert txn == txd
            assert sn == sd
            assert txhn == txhd
        else:
            assert txn != txd
            assert sn != sd
            assert txhn != txhd
