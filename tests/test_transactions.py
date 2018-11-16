from tests import EPOCH_CLI, ACCOUNT
from aeternity.signing import Account
from aeternity import transactions


def test_transaction_spend():

    recipient_id = Account.generate().get_address()
    # account_id, recipient_id, amount, payload, fee, ttl, nonce
    tts = [
        {
            "native": (ACCOUNT.get_address(), recipient_id, 1000, "payload", 1, 100, 5555),
            "debug": (ACCOUNT.get_address(), recipient_id, 1000, "payload", 1, 100, 5555),
            "match": True
        }, {
            "native": (ACCOUNT.get_address(), recipient_id, 9845, "another payload", 1, 500, 1241),
            "debug": (ACCOUNT.get_address(), recipient_id, 9845, "another payload", 1, 500, 1241),
            "match": True
        }, {
            "native": (ACCOUNT.get_address(), recipient_id, 9845, "another payload", 1, 500, 32131),
            "debug": (ACCOUNT.get_address(), Account.generate().get_address(), 9845, "another payload", 1, 500, 32131),
            "match": False
        }, {
            "native": (ACCOUNT.get_address(), recipient_id, 410000, "another payload", 100, 500, 1241),
            "debug": (ACCOUNT.get_address(), recipient_id, 410000, "another payload", 100, 500, 1241),
            "match": True
        },
    ]

    for tt in tts:
        # get a native transaction
        txbn = transactions.TxBuilder(api=EPOCH_CLI, native=True)
        txn = txbn.tx_spend(tt["native"][0], tt["native"][1], tt["native"][2], tt["native"][3], tt["native"][4], tt["native"][5], tt["native"][6])
        # get a debug transaction
        txbd = transactions.TxBuilder(api=EPOCH_CLI, native=False)
        txd = txbd.tx_spend(tt["debug"][0], tt["debug"][1], tt["debug"][2], tt["debug"][3], tt["debug"][4], tt["debug"][5], tt["debug"][6])
        # theys should be the same
        if tt["match"]:
            assert txn == txd
        else:
            assert txn != txd
