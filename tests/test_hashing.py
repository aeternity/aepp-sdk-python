from aeternity import hashing, transactions
from pytest import raises


def test_hashing_name_id():
    assert hashing.name_id('aeternity.chain') == 'nm_S4ofw6861biSJrXgHuJPo7VotLbrY8P9ngTLvgrRwbDEA3svc'
    assert hashing.name_id('apeunit.chain') == 'nm_vXDbXQHeSqLUwXdYMioZdg4i1AizRR6kH5bzj16zzUN7gdFri'
    assert hashing.name_id('abc.chain') != 'nm_S4ofw6861biSJrXgHuJPo7VotLbrY8P9ngTLvgrRwbDEA3svc'


def test_hashing_rlp():
    args = [
        {
            "data": ("tx", [b"a", b"b", 1, 0, False, True]),
            "rlp": "tx_xmFiAYCAAXNBplc=",
        },
        {
            "data": ("th", [b"a", b"b", 1, 0, False, True]),
            "rlp": "th_rCDULgdVmqKQR6W",
        },
    ]

    for a in args:
        prefix, data = a.get("data")
        assert hashing.encode_rlp(prefix, data) == a.get("rlp")

    with raises(TypeError):
        hashing.encode_rlp("tx", "a string") # valid prefix wrong data
    with raises(ValueError):
        hashing.encode_rlp(None, [1, b'a'])
    with raises(ValueError):
        hashing.encode_rlp("eg", [1, b'a'])

def test_hashing_base64():
    args = [
        {
            "data": "sample_data".encode('utf8'),
            "b64": "c2FtcGxlX2RhdGG8Ktkc"
        }
    ]

    for a in args:
        assert a.get("b64") == hashing._base64_encode(a.get("data"))
        assert a.get("data") == hashing._base64_decode(a.get("b64"))

    args = [
        None,
        "",
        "abcdzz",
        "c2FtcGxlX2RhdGG8Ktka"
    ]

    for a in args:
        with raises(ValueError):
            hashing._base64_decode(a)


def test_hashing_base58_encode():

    inputs = [
        {
            "data": "test".encode("utf-8"),
            "prefix": "th",
            "hash": "LUC1eAJa5jW",
            "match": True,
            "raise_error": False,
        },
        {
            "data": "test".encode("utf-8"),
            "prefix": "th",
            "hash": "LUC1eAJa",
            "match": False,
            "raise_error": True,

        },
        {
            "data": "aeternity".encode("utf-8"),
            "prefix": "th",
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
            with raises(TypeError):
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


def test_hashing_committment_id():

    tests = [
        {
            "domain": "aeternity.chain",
            "salt": 10692426485854419779,
            "commitment_id": "cm_j5Aa3senWdNskwSSHh3M182ucbqrAaSE5DVjejM8fBCgR97kq"
        },
        {
            "domain": "whatever.chain",
            "salt": 4703192432112,
            "commitment_id": "cm_2Hd42FoCDfYxcG3MyZkiN9wXiBKfHHzBWycEvrazPYgoEh1ien"
        },
        {
            "domain": "aepps.chain",
            "salt": 723907012945811264198,
            "commitment_id": "cm_7aMmYzWVGK2t6gqWYD9WFbwHWaLzcux6t63i2J7VHPZfcuzjs"
        },
    ]

    for t in tests:
        cid, salt = hashing.commitment_id(t.get("domain"), t.get("salt"))
        assert t.get("commitment_id") == cid
