from aeternity import hashing


def is_valid_hash(hash_str, prefix=None):
    """
    Validate an aeternity hash, optionally restrict to a specific prefix.
    The validation will check if the hash parameter is of the form prefix_hash
    and that the hash is valid according to the decode function.
    :param hash_str: the hash to validate
    :param prefix: the prefix to restrict the validation to
    """
    try:
        hashing.decode(hash_str)
        if prefix is not None and hash_str[0:2] != prefix:
            raise ValueError('Invalid prefix')
        return True
    except ValueError as e:
        return False
