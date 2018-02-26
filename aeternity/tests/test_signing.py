from aeternity.signing import base58encode, base58decode


def test_b58_encode():
    assert base58encode(b'@a') == '5uA'

def test_b58_decode():
    assert base58decode('5uA') == b'@a'

def test_b58_roundtrip():
    assert base58decode(base58encode(b'KAPOW')) == b'KAPOW'
