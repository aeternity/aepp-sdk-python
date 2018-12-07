from tests import ACCOUNT, EPOCH_CLI
from aeternity.signing import Account
from aeternity.epoch import EpochClient
from aeternity.config import Config

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


def test_epoch_offline():
    new_cli = EpochClient(offline=True, configs=Config(external_url="no", internal_url="no"))
    tx = new_cli.tx_builder.tx_spend(ACCOUNT.get_address(), Account.generate().get_address(), 10, "", 20000, 0, 10)
    tx_signed, sg, tx_hash = new_cli.sign_transaction(ACCOUNT, tx)
    assert len(tx_signed) > 0
