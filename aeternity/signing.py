alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def base58encode(bytes):
    accu = sum(i << idx * 8 for idx, i in enumerate(reversed(bytes)))
    if accu == 0:
        return alphabet[0]
    retval = ''
    while accu > 0:
        accu, b58 = divmod(accu, 58)
        retval = alphabet[b58] + retval
    return retval


def base58decode(base58str):
    retval = b''
    accu = 0
    for c in base58str:
        accu += accu * 57 + alphabet.index(c)
    while accu > 0:
        accu, b256 = divmod(accu, 256)
        retval = bytes([b256]) + retval
    return retval
