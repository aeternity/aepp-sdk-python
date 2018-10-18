from aeternity import hashing
import validators


def is_valid_hash(hash_str, prefix=None):
    """
    Validate an aeternity hash, optionally restrict to a specific prefix.
    The validation will check if the hash parameter is of the form prefix_hash
    and that the hash is valid according to the decode function.
    :param hash_str: the hash to validate
    :param prefix: the prefix to restrict the validation to
    """
    try:
        # decode the hash
        hashing.decode(hash_str)
        # if prefix is not set then is valid
        if prefix is None:
            return True
        # let's check the prefix
        if not isinstance(prefix, list):
            prefix = [prefix]
        # if a match is not found then raise ValueError
        match = False
        for p in prefix:
            match = match or prefix_match(p, hash_str)
        if not match:
            raise ValueError('Invalid prefix')
        # a match was found
        return True
    except ValueError as e:
        return False


def prefix_match(prefix, obj):
    """
    Check if an hash prefix matches:
    example: prefix_match(hash, "ak") will match "ak_123" but not "ak123"
    """
    if obj is None:
        return False
    return obj.startswith(f"{prefix}_")


def is_valid_aens_name(domain_name):
    """
    Test if the provided name is valid for the aens system
    """
    # TODO: validate according to the spec!
    # TODO: https://github.com/aeternity/protocol/blob/master/AENS.md#name

    if domain_name is None or not validators.domain(domain_name) or not domain_name.endswith(('.aet', '.test')):
        return False
    return True
