
from aeternity.tests import PUBLIC_KEY, PRIVATE_KEY
from aeternity.epoch import EpochClient
from aeternity.signing import KeyPair


def test_create_transaction_signing():
    client = EpochClient()
    # generate a new keypair
    new_keypair = KeyPair.generate()
    receiver_address = new_keypair.get_address()
    # get the test keypair
    keypair = KeyPair.from_public_private_key_strings(PUBLIC_KEY, PRIVATE_KEY)
    # create a spend transaction
    transaction = client.create_spend_transaction(PUBLIC_KEY, receiver_address, 321)
    signed_transaction, b58signature = keypair.sign_transaction(transaction)
    # post the transaction
    result = client.send_signed_transaction(signed_transaction)
    assert result is not None
    assert result.tx_hash is not None
    print(result)

    # make sure this works for very short block times
    client.wait_for_next_block(polling_interval=0.01)
    spend_tx = client.get_transaction_by_transaction_hash(result.tx_hash, tx_encoding='json')
    assert spend_tx.transaction['signatures'][0] == b58signature
