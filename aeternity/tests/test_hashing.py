from aeternity import hashing


def test_hashing_name_hashing():
    assert hashing.namehash_encode('nm', 'welghmolql.aet') == 'nm_2KrC4asc6fdv82uhXDwfiqB1TY2htjhnzwzJJKLxidyMymJRUQ'
    assert hashing.namehash_encode('pp', 'welghmolql.aet') == 'pp_2KrC4asc6fdv82uhXDwfiqB1TY2htjhnzwzJJKLxidyMymJRUQ'
    assert hashing.namehash_encode('nm', 'abc.aet') != 'nm_2KrC4asc6fdv82uhXDwfiqB1TY2htjhnzwzJJKLxidyMymJRUQ'


def test_hashing_base58_encode():

    inputs = [
        {
            "data": "test".encode("utf-8"),
            "prefix": "tt",
            "hash": "LUC1eAJa5jW",
            "match": True,
            "raise_error": False,
        },
        {
            "data": "test".encode("utf-8"),
            "prefix": "tt",
            "hash": "LUC1eAJa",
            "match": False,
            "raise_error": True,

        },
        {
            "data": "aeternity".encode("utf-8"),
            "prefix": "aa",
            "hash": "97Wv2fcowb3y3qVnDC",
            "match": True,
            "raise_error": False,
        },
    ]

    for i in inputs:
        try:
            h = hashing._base58_encode(i.get("data"))
            assert (h == i.get("hash")) is i.get("match")
            e = hashing.encode(i.get("prefix"), i.get("data"))
            assert (e == f'{i.get("prefix")}_{i.get("hash")}') is i.get("match")
            o = hashing._base58_decode(i.get("hash"))
            assert (o == i.get("data")) is i.get("match")
        except Exception as e:
            assert i.get("raise_error") is True
