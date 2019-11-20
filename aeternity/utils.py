import validators

from decimal import Decimal
from aeternity import hashing


def is_valid_hash(hash_str: str, prefix: str = None) -> bool:
    """
    Validate an aeternity hash, optionally restrict to a specific prefix.
    The validation will check if the hash parameter is of the form prefix_hash
    and that the hash is valid according to the decode function.
    :param hash_str: the hash to validate
    :param prefix: the prefix to restrict the validation to
    :return: true if it is valid false otherwise
    """
    try:
        if hash_str is None:
            return False
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
    except ValueError:
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
    if domain_name is None or not validators.domain(domain_name.lower()) or (
            not domain_name.endswith(('.chain')) and not domain_name.endswith(('.test'))):
        return False
    return True


def format_amount(value: int, precision: int = -18, unit_label: str = "AE") -> str:
    """
    Format a number as ERC20 token (1e18) and adding the unit

    For example, if you want to format the amount 1000000 in microAE
    you can use format_amount(1000000, -6, 'microAE')

    If the value is None or <= 0 the function returns 0

    :param value: the value to format
    :param precision: the precision to use, default -18
    :param unit_label: the label to use to format the value, default AE
    :return: a string with the value formatted using precision and unit_label
    """
    if value is None or value <= 0:
        return f"0{unit_label}"
    value = Decimal(value).scaleb(precision)
    # remove trailing 0
    value = str(value).rstrip('0').rstrip('.')
    return f"{value}{unit_label}"


def amount_to_aettos(value) -> int:
    """
    Transform a value describing an amount in AE to aettos.
    Supported amount format are
    - floats: ex 1.2 3e12
    - string: ex 12AE 12ae 12Ae
    - int: will return the same number

    :param value: the value to transform
    :return: the amount ins aettos
    :raises TypeError: if the input value is not recognized or if the amount is lt 0 or amount is gt 1e28

    for additional reference check https://docs.python.org/3/library/decimal.html#decimal.Decimal.quantize

    """
    amount = None
    if isinstance(value, int):
        amount = value
    elif isinstance(value, str):
        clean_val = value.strip().lower()
        if clean_val.isdigit():
            amount = int(clean_val)
        else:
            clean_val = clean_val[:-2] if clean_val.endswith("ae") else clean_val
            try:
                amount = Decimal(clean_val).scaleb(18).quantize(Decimal('1'))
            except Exception as e:
                raise TypeError(f"Invalid value for amount: {value}, {e}")
    elif isinstance(value, float):
        amount = Decimal(f'{value}').scaleb(18).quantize(Decimal('1'))
    else:
        raise TypeError(f"Invalid value for amount: {value}")
    # validate the number
    if amount < 0:
        raise TypeError("Amount values must be greater then 0")
    return int(amount)


def _amounts_to_aettos(*values):
    """
    Shortcut function to convert multiple values in one call
    """
    return [amount_to_aettos(x) for x in values]
