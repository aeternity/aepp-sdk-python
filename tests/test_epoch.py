from tests import ACCOUNT, NODE_CLI
from aeternity.signing import Account

# from aeternity.exceptions import TransactionNotFoundException


def _test_node_spend():
    account = Account.generate().get_address()
    NODE_CLI.spend(ACCOUNT, account, 100)
    account = NODE_CLI.get_account_by_pubkey(pubkey=account)
    balance = account.balance
    assert balance > 0


def test_node_spend_internal():
    NODE_CLI.set_native(False)
    _test_node_spend()


def test_node_spend_native():
    NODE_CLI.set_native(True)
    _test_node_spend()
