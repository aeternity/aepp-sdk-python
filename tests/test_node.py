from aeternity.signing import Account

# from aeternity.exceptions import TransactionNotFoundException


def _test_node_spend(chain_fixture):
    account = Account.generate().get_address()
    chain_fixture.NODE_CLI.spend(chain_fixture.ACCOUNT, account, 100)
    account = chain_fixture.NODE_CLI.get_account_by_pubkey(pubkey=account)
    balance = account.balance
    assert balance > 0


def test_node_spend_internal(chain_fixture):
    chain_fixture.NODE_CLI.set_native(False)
    _test_node_spend()


def test_node_spend_native(chain_fixture):
    chain_fixture.NODE_CLI.set_native(True)
    _test_node_spend()
