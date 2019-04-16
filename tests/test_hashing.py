from aeternity import hashing, transactions
from pytest import raises


def test_hashing_name_hashing():
    assert hashing.namehash_encode('nm', 'welghmolql.test') == 'nm_Ziiq3M9ASEHXCV71qUNde6SsomqwZjYPFvnJSvTkpSUDiXqH3'
    assert hashing.namehash_encode('pp', 'welghmolql.test') == 'pp_Ziiq3M9ASEHXCV71qUNde6SsomqwZjYPFvnJSvTkpSUDiXqH3'
    assert hashing.namehash_encode('nm', 'abc.test') != 'nm_2KrC4asc6fdv82uhXDwfiqB1TY2htjhnzwzJJKLxidyMymJRUQ'


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


def test_hashing_transactions_binary():
    tts = [
        {"in": "test", "bval": "test".encode("utf-8"), "match": True, "err": False},
        {"in": "test", "bval": "t".encode("utf-8"), "match": False, "err": False},
        {"in": 8, "bval": b'\x08', "match": True, "err": False},
        {"in": 1000, "bval": b'\x00\x03\xe8', "match": False, "err": False},  # with padding
        {"in": 1000, "bval": b'\x03\xe8', "match": True, "err": False},  # without padding
        {"in": 1000, "bval": b'\x03\xe8', "match": True, "err": False},  # without padding
        {"in": 13141231, "bval": b'\xc8\x84\xef', "match": True, "err": False},  # without padding
        {"in": ["312321"], "bval": b'', "match": False, "err": True},
        {"in": b'\x00\x16\xba\x14\xfb', "bval": b'\x00\x16\xba\x14\xfb', "match": True, "err": False},
        {"in": b'\x16\xba\x14\xfb', "bval": b'\x00\x16\xba\x14\xfb', "match": False, "err": False},
    ]

    for tt in tts:
        print(tt)
        if tt['err']:
            with raises(ValueError):
                transactions._binary(tt['in'])
        elif tt['match']:
            assert transactions._binary(tt['in']) == tt['bval']
        elif not tt['match']:
            assert transactions._binary(tt['in']) != tt['bval']
        else:
            assert False


def test_hashing_contract_id():
    # TODO: add more scenarios
    # owner_id, nonce -> contract_id, match
    tt = [
        ('ak_P1hn3JnJXcdx8USijBcgZHLgvZywH5PbjQK5G1iZaEu9obHiH', 2, 'ct_5ye5dEQwtCrRhsKYq8BprAMFptpY59THUyTxSBQKpDTcywEhk', True),
        ('ak_P1hn3JnJXcdx8USijBcgZHLgvZywH5PbjQK5G1iZaEu9obHiH', 1, 'ct_5ye5dEQwtCrRhsKYq8BprAMFptpY59THUyTxSBQKpDTcywEhk', False),
    ]

    for t in tt:
        assert (hashing.contract_id(t[0], t[1]) == t[2]) == t[3]


def test_hashing_oracle_query_id():
    # TODO: add more scenarios
    # sender_id, nonce, oracle_id -> query_id, match
    tt = [
        ('ak_2ZjpYpJbzq8xbzjgPuEpdq9ahZE7iJRcAYC1weq3xdrNbzRiP4', 1, 'ok_2iqfJjbhGgJFRezjX6Q6DrvokkTM5niGEHBEJZ7uAG5fSGJAw1',
         'oq_2YvZnoohcSvbQCsPKSMxc98i5HZ1sU5mR6xwJUZC3SvkuSynMj', True),
    ]

    for t in tt:
        assert (hashing.oracle_query_id(t[0], t[1], t[2]) == t[3]) == t[4]


def test_hashing_oracle_id():
    # account_id, -> oracle_id, match
    tt = [
        ('ak_2iqfJjbhGgJFRezjX6Q6DrvokkTM5niGEHBEJZ7uAG5fSGJAw1', 'ok_2iqfJjbhGgJFRezjX6Q6DrvokkTM5niGEHBEJZ7uAG5fSGJAw1', True),
    ]

    for t in tt:
        assert (hashing.oracle_id(t[0]) == t[1]) == t[2]


def test_hashing_committment_id(random_domain):

    tests = [
        {
            "domain": "aeternity.test",
            "salt": 10692426485854419779,
            "commitment_id": "cm_2by2qwnum96Z78WSFRJwhsC5qFzDgatrKk7PfH3yZ2wMBmsZF2"
        },
        {
            "domain": "whatever.test",
            "salt": 4703192432112,
            "commitment_id": "cm_2GDk2XGBEqgNKM2sz63EVhsWi6ZGxjR1M7TMFZQvcBUin1As6"
        },
        {
            "domain": "aepps.test",
            "salt": 723907012945811264198,
            "commitment_id": "cm_pQu4wAuiyhe1mHqZzh3yNA4JwBPaess3MY7MnZFG9vsFjD5yE"
        },
    ]

    for t in tests:
        cid, salt = hashing.commitment_id(t.get("domain"), t.get("salt"))
        assert t.get("commitment_id") == cid
