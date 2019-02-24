from aeternity.signing import Account
import pytest
# from aeternity.exceptions import TransactionNotFoundException


def _test_node_spend(node_cli, sender_account):
    account = Account.generate().get_address()
    node_cli.spend(sender_account, account, 100)
    account = node_cli.get_account_by_pubkey(pubkey=account)
    balance = account.balance
    assert balance > 0


@pytest.mark.skip('Debug transaction disabled')
def test_node_spend_debug(chain_fixture):
    chain_fixture.NODE_CLI.set_native(False)
    _test_node_spend(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)


def test_node_spend_native(chain_fixture):
    chain_fixture.NODE_CLI.set_native(True)
    _test_node_spend(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)
