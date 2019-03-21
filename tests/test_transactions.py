
from aeternity.signing import Account
from aeternity import transactions, exceptions
import pytest


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


@pytest.mark.skip("Debug trasnsaction disabled")
def test_transaction_spend(chain_fixture):

    recipient_id = Account.generate().get_address()
    # account_id, recipient_id, amount, payload, fee, ttl, nonce
    tts = [
        {
            "native": (chain_fixture.ACCOUNT.get_address(), recipient_id, 1000, "payload", 1, 100, 5555),
            "debug": (chain_fixture.ACCOUNT.get_address(), recipient_id, 1000, "payload", 1, 100, 5555),
            "match": True
        }, {
            "native": (chain_fixture.ACCOUNT.get_address(), recipient_id, 9845, "another payload", 1, 500, 1241),
            "debug": (chain_fixture.ACCOUNT.get_address(), recipient_id, 9845, "another payload", 1, 500, 1241),
            "match": True
        }, {
            "native": (chain_fixture.ACCOUNT.get_address(), recipient_id, 9845, "another payload", 1, 500, 32131),
            "debug": (chain_fixture.ACCOUNT.get_address(), Account.generate().get_address(), 9845, "another payload", 1, 500, 32131),
            "match": False
        }, {
            "native": (chain_fixture.ACCOUNT.get_address(), recipient_id, 410000, "another payload", 100, 500, 1241),
            "debug": (chain_fixture.ACCOUNT.get_address(), recipient_id, 410000, "another payload", 100, 500, 1241),
            "match": True
        },
    ]

    for tt in tts:
        # get a native transaction
        txbn = transactions.TxBuilder()
        txn = txbn.tx_spend(tt["native"][0], tt["native"][1], tt["native"][2], tt["native"][3], tt["native"][4], tt["native"][5], tt["native"][6])
        # get a debug transaction
        txbd = transactions.TxBuilder()
        txd = txbd.tx_spend(tt["debug"][0], tt["debug"][1], tt["debug"][2], tt["debug"][3], tt["debug"][4], tt["debug"][5], tt["debug"][6])
        # theys should be the same
        if tt["match"]:
            assert txn == txd
        else:
            assert txn != txd


@pytest.mark.skip("Debug trasnsaction disabled")
def test_transaction_oracle_register(chain_fixture):
    # account_id, recipient_id, amount, payload, fee, ttl, nonce
    tts = [
        {
            "tx": "tx_oracle_register",
            "native": {'account_id': 'ak_2bstpmUDaNcc4jvNENHD9Mfxf55YnK4W24RkGCrHyeVESYvS43',
                       'query_format': "{'city': str}", 'response_format': "{'temp_c': int}",
                       'query_fee': 10, 'ttl_type': 'delta', 'ttl_value': 500, 'vm_version': 0, 'fee': 10, 'ttl': 505, 'nonce': 1},
            "debug": {'account_id': 'ak_2bstpmUDaNcc4jvNENHD9Mfxf55YnK4W24RkGCrHyeVESYvS43',
                      'query_format': "{'city': str}", 'response_format': "{'temp_c': int}",
                      'query_fee': 10, 'ttl_type': 'delta', 'ttl_value': 500, 'vm_version': 0, 'fee': 10, 'ttl': 505, 'nonce': 1},
            "match": True
        },
        {
            "tx": "tx_oracle_register",
            "native": {'account_id': 'ak_2bstpmUDaNcc4jvNENHD9Mfxf55YnK4W24RkGCrHyeVESYvS43',
                       'query_format': "{'city': str}", 'response_format': "{'temp_c': int}",
                       'query_fee': 10, 'ttl_type': 'delta', 'ttl_value': 500, 'vm_version': 0, 'fee': 10, 'ttl': 505, 'nonce': 1},
            "debug": {'account_id': 'ak_2bstpmUDaNcc4jvNENHD9Mfxf55YnK4W24RkGCrHyeVESYvS43',
                      'query_format': "{'city': str}", 'response_format': "{'temp_c': int}",
                      'query_fee': 11, 'ttl_type': 'delta', 'ttl_value': 500, 'vm_version': 0, 'fee': 10, 'ttl': 505, 'nonce': 1},
            "match": False
        }
    ]
    _execute_test(tts, chain_fixture.NODE_CLI)
