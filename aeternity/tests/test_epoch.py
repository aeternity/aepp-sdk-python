from aeternity.tests import ACCOUNT, EPOCH_CLI
from aeternity.signing import Account

# from aeternity.exceptions import TransactionNotFoundException


def test_epoch_spend():
    account = Account.generate().get_address()
    EPOCH_CLI.spend(ACCOUNT, account, 100)
    account = EPOCH_CLI.get_account_by_pubkey(pubkey=account)
    balance = account.balance
    assert balance > 0
