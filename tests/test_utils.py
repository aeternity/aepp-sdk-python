
from aeternity import utils


def test_utils_is_valid_hash():
    # input (hash_str, prefix, expected output)
    args = [
        ('ak_me6L5SSXL4NLWv5EkQ7a16xaA145Br7oV4sz9JphZgsTsYwGC', None, True),
        ('ak_me6L5SSXL4NLWv5EkQ7a16xaA145Br7oV4sz9JphZgsTsYwGC', 'ak', True),
        ('ak_me6L5SSXL4NLWv5EkQ7a16xaA145Br7oV4sz9JphZgsTsYwGC', 'bh', False),
        ('ak_me6L5SSXL4NLWv5EkQ7a16xaA145Br7oV4sz9JphZgsTsYwYC', None, False),
        ('ak_me6L5SSXL4NLWv5EkQ7a18xaA145Br7oV4sz9JphZgsTsYwGC', None, False),
        ('kh_vzUC2jVuAfpBC3tMAHhxwxJnTFymckNYeQ5TWZua1pydabqNu', None, True),
        ('kh_vzUC2jVuAfpBC3tMAHhxwxJnTFymckNYeQ5TWZua1pydabqNu', ["kh", "mh"], True),
        ('mh_vzUC2jVuAfpBC3tMAHhxwxJnTFymckNYeQ5TWZua1pydabqNu', ["kh", "mh"], True),
        ('th_vzUC2jVuAfpBC3tMAHhxwxJnTFymckNYeQ5TWZua1pydabqNu', ["kh", "mh"], False),
        ('th_YqPSTzs73PiKFhFcALYWWu41uNLc6yp63ZC35jzzuJYA9PMui', None, True),
        ('th_YqPSTzs73PiKFhFcALYWWu41uNLc6yp63ZC35jzzuJYA9PMui', ["th"], True),
    ]

    for a in args:
        got = utils.is_valid_hash(a[0], a[1])
        expected = a[2]
        assert got == expected


def test_utils_is_valid_name():
    # input (hash_str, prefix, expected output)
    args = [
        ('valid.test', True),
        ('v.test', True),
        ('isaverylongnamethatidontknow.test', True),
        ('0123.test', True),
        ('0alsoGOod.test', True),
        ('valid.test', True),
        ('valid.test', True),
        ('aeternity.com', False),
        ('aeternity.aet', False),
        ('om', False),
        (None, False),
        (".o.test", False),
        ("-o.test", False),
    ]

    for a in args:
        got = utils.is_valid_aens_name(a[0])
        expected = a[1]
        assert got == expected


def test_utils_format_amount():
    # input (hash_str, prefix, expected output)
    args = [
        (1000000000000000000, "1AE"),
        (2000000000000000000, "2AE"),
        (20000000000000000000, "20AE"),
        (20100000000000000000, "20.1AE"),
        (2000000000000000, "0.002AE"),
        (1116270000000000000000, "1116.27AE"),
        (28000000001760, "0.00002800000000176AE"),
        (0, "0AE")

    ]

    for a in args:
        got = utils.format_amount(a[0])
        expected = a[1]
        assert got == expected
