from aeternity import EpochClient
from aeternity.signing import KeyPair

def test_create_transaction_signing():
    client = EpochClient()

    new_keypair = KeyPair.generate()
    receiver_address = new_keypair.get_address()

    keypair = KeyPair.read_from_dir('/home/tom/data/aeternity/epoch/_build/dev1/rel/epoch/data/aecore/keys/', 'secret')

    transaction = client.create_transaction(receiver_address, 10)
    signed_transaction = keypair.sign_transaction(transaction)
    result = client.send_signed_transaction(signed_transaction)
    assert result == {}
