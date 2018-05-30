
from aeternity.tests import PUBLIC_KEY, PRIVATE_KEY
from aeternity.epoch import EpochClient
from aeternity.signing import KeyPair


def test_create_transaction_signing():
    client = EpochClient()

    new_keypair = KeyPair.generate()
    receiver_address = new_keypair.get_address()

    keypair = KeyPair.from_public_private_key_strings(PUBLIC_KEY, PRIVATE_KEY)

    transaction = client.create_spend_transaction(PUBLIC_KEY, receiver_address, 321)
    signed_transaction, b58signature = keypair.sign_transaction(transaction)

    result = client.send_signed_transaction(signed_transaction)
    assert result == {}

    # make sure this works for very short block times
    client.wait_for_next_block(polling_interval=0.01)
    next_block = client.get_latest_block()
    next_next_block = client.get_latest_block()
    all_transactions = next_block.transactions + next_next_block.transactions
    import json
    print(json.dumps(all_transactions, indent=2))
    # find the transaction that is the spend transaction we just submitted
    spend_tx = next(tx for tx in all_transactions if (tx['tx']['type']) == 'spend_tx')
    print(json.dumps(spend_tx, indent=2))
    assert spend_tx['signatures'][0] == b58signature


