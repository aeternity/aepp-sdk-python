from . import conftest

"""
WARNING: this file is used as source for the tutorial in
docs/intro/tutorial01-spend.rst
line numbers are important
verify the doc file for consistency after edit
"""

from aeternity.node import NodeClient, Config
from aeternity.signing import Account
from aeternity import utils
import os

def test_node_spend(chain_fixture):

    NODE_URL = os.environ.get('TEST_URL', 'https://testnet.aeternity.io')

    node_cli = NodeClient(Config(
        external_url=NODE_URL,
        blocking_mode=True,
    ))

    # generate ALICE account 
    alice = Account.generate()

    # generate BOB account
    bob = Account.generate()

    # retrieve the balances for the accounts
    bob_balance = node_cli.get_balance(bob)
    alice_balance = node_cli.get_balance(alice)

    # print the balance of the two accounts
    print(f"Alice address is {alice.get_address()}")
    print(f"with balance {utils.format_amount(alice_balance)}")
    print(f"Bob address is {bob.get_address()}")
    print(f"with balance {utils.format_amount(bob_balance)}")

    # begin - tests execution section
    # top up the account from the test suite account,
    # outside the tests use the faucet to top_up an account
    node_cli.spend(chain_fixture.BOB, alice.get_address(), "5AE")
    #  end - tests execution section

    #TODO pause the execution while using the faucet
    # execute the spend transaction
    tx = node_cli.spend(alice, bob.get_address(), "3AE")
    print(f"transaction hash: {tx.hash}")
    print(f"inspect transaction at {NODE_URL}/v2/transactions/{tx.hash}")

    # begin - tests execution section
    assert bob.get_address() == tx.data.tx.data.recipient_id
    assert alice.get_address() == tx.data.tx.data.sender_id
    #  end - tests execution section

    print(f"Alice balance is {utils.format_amount(alice_balance)}")
    print(f"Bob balance is {utils.format_amount(bob_balance)}")

    # begin - tests execution section
    assert bob_balance > 0
    assert alice_balance > 0
    assert alice_balance < bob_balance
    #  end - tests execution section

