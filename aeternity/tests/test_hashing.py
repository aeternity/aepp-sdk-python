from aeternity import hashing


def test_hashing_name_hashing():
    assert hashing.namehash_encode('nm', 'welghmolql.aet') == 'nm_2KrC4asc6fdv82uhXDwfiqB1TY2htjhnzwzJJKLxidyMymJRUQ'
    assert hashing.namehash_encode('pp', 'welghmolql.aet') == 'pp_2KrC4asc6fdv82uhXDwfiqB1TY2htjhnzwzJJKLxidyMymJRUQ'
    assert hashing.namehash_encode('nm', 'abc.aet') != 'nm_2KrC4asc6fdv82uhXDwfiqB1TY2htjhnzwzJJKLxidyMymJRUQ'
