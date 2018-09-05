from aeternity.tests import KEYPAIR
from aeternity.epoch import EpochClient
from aeternity.signing import KeyPair

# from aeternity.exceptions import TransactionNotFoundException


def test_epoch_spend():
    client = EpochClient()
    account = KeyPair.generate().get_address()
    client.spend(KEYPAIR, account, 100)
    account = client.get_account_by_pubkey(pubkey=account)
    client.wait_for_next_block()
    balance = account.balance

    assert balance > 0


