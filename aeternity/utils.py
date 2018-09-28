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
        hashing.decode(hash_str)
        if prefix is not None and hash_str[0:2] != prefix:
            raise ValueError('Invalid prefix')
        return True
    except ValueError as e:
        return False


def is_valid_aens_name(domain_name):
    """
    Test if the provided name is valid for the aens system
    """
    # TODO: validate according to the spec!
    # TODO: https://github.com/aeternity/protocol/blob/master/AENS.md#name

    if domain_name is None or not validators.domain(domain_name) or not domain_name.endswith(('.aet', '.test')):
        return False
    return True
