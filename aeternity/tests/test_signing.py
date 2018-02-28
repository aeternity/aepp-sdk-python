from aeternity import EpochClient
from aeternity.signing import base58encode, base58decode, KeyPair


def test_b58_encode():
    assert base58encode(b'@a') == '5uA'

def test_b58_decode():
    assert base58decode('5uA') == b'@a'

def test_b58_roundtrip():
    assert base58decode(base58encode(b'KAPOW')) == b'KAPOW'

def test_create_transaction_signing():
    client = EpochClient()
    transaction = client.create_transaction(client.get_pubkey(), 10)
    keypair = KeyPair.read_from_dir('/home/tom/data/aeternity/epoch/_build/dev1/rel/epoch/data/aecore/keys/', 'secret')
    signed_transaction = keypair.sign_transaction(transaction)
    print('signed transaction')
    print(signed_transaction)
    result = client.send_signed_transaction(signed_transaction)
    print('sending signed transaction')
    print(result)
    assert False
