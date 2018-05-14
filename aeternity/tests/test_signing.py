import base58
import os

from aeternity import EpochClient
from aeternity.epoch import SpendTx
from aeternity.signing import KeyPair


def test_create_transaction_signing():
    client = EpochClient()

    new_keypair = KeyPair.generate()
    receiver_address = new_keypair.get_address()

    pub_key = os.environ.get('WALLET_PUB')
    priv_key = os.environ.get('WALLET_PRIV')
    keypair = KeyPair.from_public_private_key_strings(pub_key, priv_key)

    transaction = client.create_spend_transaction(receiver_address, 10)
    signed_transaction, b58signature = keypair.sign_transaction(transaction)
    result = client.send_signed_transaction(signed_transaction)
    assert result == {}

    current_block = client.get_latest_block()
    # make sure this works for very short block times
    client.wait_for_next_block(polling_interval=0.01)
    next_block = client.get_latest_block()
    next_next_block = client.get_latest_block()
    all_transactions = next_block.transactions + next_next_block.transactions
    # find the transaction that is the spend transaction we just submitted
    spend_tx = next(tx for tx in all_transactions if type(tx.tx) == SpendTx)
    assert spend_tx.signatures[0] == b58signature
