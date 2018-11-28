from tests import ACCOUNT, EPOCH_CLI
from aeternity.signing import Account

# from aeternity.exceptions import TransactionNotFoundException


def _test_epoch_spend():
    account = Account.generate().get_address()
    EPOCH_CLI.spend(ACCOUNT, account, 100)
    account = EPOCH_CLI.get_account_by_pubkey(pubkey=account)
    balance = account.balance
    assert balance > 0


def test_epoch_spend_internal():
    EPOCH_CLI.set_native(False)
    _test_epoch_spend()


def test_epoch_spend_native():
    EPOCH_CLI.set_native(True)
    _test_epoch_spend()
