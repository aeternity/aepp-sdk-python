from aeternity import utils
import pytest
import random


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
    # TODO: 
    args = [
        ('valid.test', True),
        ('v.test', True),
        ('isaverylongnamethatidontknow.test', True),
        ('0123.test', True),
        ('0alsoGOod.test', True),
        ('valid.test', True),
        ('valid.test', True),
        ('aeternity.com', False),
        ('aeternity.chain', True),
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



def test_utils_amount_to_aettos():
    args = [
        ("1.2AE", 1200000000000000000),
        ("1.2ae", 1200000000000000000),
        (" 1.2ae  ", 1200000000000000000),
        ("1.25ae", 1250000000000000000),
        (1.3, 1300000000000000000),
        (10, 10),
        (-1, TypeError()),
        ("10", 10),
        (" 1000  ", 1000),
        ("1001  ", 1001),
        ("   1002", 1002),
        ("1,25ae", TypeError()),
        ("1ae", 1000000000000000000),
        ("0.000000005", 5000000000),
        ("0", 0),
        (0, 0),
    ]


    # TODO: test more float 
    for i in range(10000):
        val = random.randint(0, 1000000000000000000000000)
        args.append((utils.format_amount(val), val))

    for i in range(10000):
        val = random.randint(0, 1000000)
        args.append((utils.format_amount(val), val))

    # the default context has 28 for max prcision
    # therefore anything greater than 1e28 will fail
    for i in range(10000):
        val = random.randint(1000000000000000000, 10000000000000000000000000000)
        args.append((utils.format_amount(val), val))

    for a in args:
        expected = a[1]
        if issubclass(type(expected), Exception):
            with pytest.raises(type(expected)):
                utils.amount_to_aettos(a[0])
        else:
            got = utils.amount_to_aettos(a[0])
            assert got == expected
