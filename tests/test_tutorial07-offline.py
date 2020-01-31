from . import conftest

"""
WARNING: this file is used as source for the tutorial in
docs/intro/tutorial07-offline.rst
line numbers are important
verify the doc file for consistency after edit
"""

from aeternity.node import NodeClient, Config
from aeternity.signing import Account
from aeternity.transactions import TxBuilder, TxSigner
from aeternity import utils, defaults, identifiers
import os

def test_tutorial_offline_tx(chain_fixture):

    # Accounts addresses
    account = Account.generate()

    # --- hide --- override the account for tests
    account = chain_fixture.ALICE
    # /--- hide ---

    # instantiate the transactions builder
    build = TxBuilder()

    # we will be creating 5 transactions for later broadcast TODO: warn about the nonce limit
    txs = []

    # each transaction is going to be a spend
    amount = utils.amount_to_aettos("0.05AE")
    payload = b''

    for i in range(5):
        # increase the account nonce
        account.nonce = account.nonce + 1
        # build the transaction
        tx = build.tx_spend(
            account.get_address(),  # sender
            Account.generate().get_address(),  # random generated recipient
            amount,
            payload,
            defaults.FEE,
            defaults.TX_TTL,
            account.nonce
        )
        # save the transaction
        txs.append(tx)

    # Sign the transactions
    # define the network_id
    network_id = identifiers.NETWORK_ID_TESTNET

    # --- hide --- override the network_id for tests
    network_id = chain_fixture.NODE_CLI.config.network_id
    # /--- hide ---

    # instantiate a transaction signer
    signer = TxSigner(account, network_id)

    # collect the signed tx for broadcast
    signed_txs = []
    # sign all transactions 
    for tx in txs:
        signature = signer.sign_transaction(tx)
        signed_tx = build.tx_signed([signature], tx)
        signed_txs.append(signed_tx)

    # Broadcast the transactions
    NODE_URL = os.environ.get('TEST_URL', 'https://testnet.aeternity.io')

    node_cli = NodeClient(Config(
        external_url=NODE_URL,
        blocking_mode=False,
    ))

    # broadcast all transactions
    for stx in signed_txs:
        node_cli.broadcast_transaction(stx)

    # verify that all transactions have been posted
    for stx in signed_txs:
        height = node_cli.wait_for_transaction(stx)
        assert(height > 0)

