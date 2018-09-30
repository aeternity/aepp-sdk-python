from aeternity.tests import KEYPAIR
from aeternity.epoch import EpochClient
from aeternity.signing import Account

# from aeternity.exceptions import TransactionNotFoundException


def test_epoch_spend():
    client = EpochClient()
    account = Account.generate().get_address()
    client.spend(KEYPAIR, account, 100)
    client.wait_for_next_block()
    account = client.get_account_by_pubkey(pubkey=account)
    balance = account.balance
    assert balance > 0
