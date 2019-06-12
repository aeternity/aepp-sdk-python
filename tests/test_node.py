from aeternity.signing import Account
import pytest
# from aeternity.exceptions import TransactionNotFoundException


def _test_node_spend(node_cli, sender_account):
    account = Account.generate().get_address()
    tx = node_cli.spend(sender_account, account, 100)
    assert account == tx.data.recipient_id
    assert sender_account.get_address() == tx.data.sender_id
    account = node_cli.get_account_by_pubkey(pubkey=account)
    balance = account.balance
    assert balance > 0


def test_node_spend_native(chain_fixture):
    _test_node_spend(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)


@pytest.mark.parametrize("height,protocol_version", [(0, 1), (1, 1), (2, 2), (3, 2), (4, 3), (5, 3)])
def test_node_get_protocol_version(chain_fixture, height, protocol_version):
    # this test assumes that the configuration of the node bein tested has the follwing configuration:
    #   hard_forks:
    #      "1": 0
    #      "2": 2
    #      "3": 4
    assert(chain_fixture.NODE_CLI.get_consensus_protocol_version(height)) == protocol_version
