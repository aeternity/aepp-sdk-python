from aeternity import identifiers

# fee calculation
BASE_GAS = 15000
GAS_PER_BYTE = 20
GAS_PRICE = 1000000000
# default relative ttl in number of blocks  for executing transaction on the chain
MAX_TX_TTL = 256
TX_TTL = 0
FEE = 0
# contracts
CONTRACT_GAS = 10000
CONTRACT_GAS_PRICE = 1000000000
CONTRACT_DEPOSIT = 0
CONTRACT_AMOUNT = 0
# calldata for the init function with no parameters
CONTRACT_INIT_CALLDATA = "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACC5yVbyizFJqfWYeqUF89obIgnMVzkjQAYrtsG9n5" + \
    "+Z6gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnHQYrA=="
# https://github.com/aeternity/protocol/blob/master/oracles/oracles.md#technical-aspects-of-oracle-operations
ORACLE_VM_VERSION = identifiers.NO_VM
ORACLE_TTL_TYPE = identifiers.ORACLE_TTL_TYPE_DELTA
ORACLE_QUERY_FEE = 0
ORACLE_TTL_VALUE = 500
ORACLE_QUERY_TTL_VALUE = 10
ORACLE_RESPONSE_TTL_VALUE = 10
# Chain
KEY_BLOCK_INTERVAL = 3  # average time between key-blocks in minutes
KEY_BLOCK_CONFIRMATION_NUM = 3  # number of key blocks to wait for to consider a key-block confirmed
# network id
NETWORK_ID = identifiers.NETWORK_ID_MAINNET
# TUNING
POLL_TX_MAX_RETRIES = 8  # used in exponential backoff when checking a transaction
POLL_TX_RETRIES_INTERVAL = 2  # in seconds
POLL_BLOCK_MAX_RETRIES = 20  # number of retries
POLL_BLOCK_RETRIES_INTERVAL = 30  # in seconds
# channels
CHANNEL_ENDPOINT = 'channel'
CHANNEL_URL = 'ws://127.0.0.1:3014'
# Generalized accounts
GA_AUTH_FUNCTION = "authorize"
GA_MAX_AUTH_FUN_GAS = 50000
GA_ACCOUNTS_NONCE = 0  # for tx in ga transactions the nonce must be 0
# Aens
# max number of block into the future that the name is going to be available
# https://github.com/aeternity/protocol/blob/master/AENS.md#aens-entry
NAME_MAX_TTL = 50000  # in blocks
NAME_MAX_CLIENT_TTL = 84600  # in seconds
NAME_FEE = 0
# see https://github.com/aeternity/aeternity/blob/72e440b8731422e335f879a31ecbbee7ac23a1cf/apps/aecore/src/aec_governance.erl#L67
NAME_FEE_MULTIPLIER = 100000000000000
NAME_FEE_BID_INCREMENT = 0.05  # the increment is in percentage
# see https://github.com/aeternity/aeternity/blob/72e440b8731422e335f879a31ecbbee7ac23a1cf/apps/aecore/src/aec_governance.erl#L272
NAME_BID_TIMEOUT_BLOCKS = 480  # ~1 day
NAME_BID_MAX_LENGTH = 12  # this is the max length for a domain to be part of a bid
# ref: https://github.com/aeternity/aeternity/blob/72e440b8731422e335f879a31ecbbee7ac23a1cf/apps/aecore/src/aec_governance.erl#L290
# bid ranges:
NAME_BID_RANGES = {
    31: 3 * NAME_FEE_MULTIPLIER,
    30: 5 * NAME_FEE_MULTIPLIER,
    29: 8 * NAME_FEE_MULTIPLIER,
    28: 13 * NAME_FEE_MULTIPLIER,
    27: 21 * NAME_FEE_MULTIPLIER,
    26: 34 * NAME_FEE_MULTIPLIER,
    25: 55 * NAME_FEE_MULTIPLIER,
    24: 89 * NAME_FEE_MULTIPLIER,
    23: 144 * NAME_FEE_MULTIPLIER,
    22: 233 * NAME_FEE_MULTIPLIER,
    21: 377 * NAME_FEE_MULTIPLIER,
    20: 610 * NAME_FEE_MULTIPLIER,
    19: 987 * NAME_FEE_MULTIPLIER,
    18: 1597 * NAME_FEE_MULTIPLIER,
    17: 2584 * NAME_FEE_MULTIPLIER,
    16: 4181 * NAME_FEE_MULTIPLIER,
    15: 6765 * NAME_FEE_MULTIPLIER,
    14: 10946 * NAME_FEE_MULTIPLIER,
    13: 17711 * NAME_FEE_MULTIPLIER,
    12: 28657 * NAME_FEE_MULTIPLIER,
    11: 46368 * NAME_FEE_MULTIPLIER,
    10: 75025 * NAME_FEE_MULTIPLIER,
    9: 121393 * NAME_FEE_MULTIPLIER,
    8: 196418 * NAME_FEE_MULTIPLIER,
    7: 317811 * NAME_FEE_MULTIPLIER,
    6: 514229 * NAME_FEE_MULTIPLIER,
    5: 832040 * NAME_FEE_MULTIPLIER,
    4: 1346269 * NAME_FEE_MULTIPLIER,
    3: 2178309 * NAME_FEE_MULTIPLIER,
    2: 3524578 * NAME_FEE_MULTIPLIER,
    1: 5702887 * NAME_FEE_MULTIPLIER,
}

# ref: https://github.com/aeternity/aeternity/blob/72e440b8731422e335f879a31ecbbee7ac23a1cf/apps/aecore/src/aec_governance.erl#L273
# name bid timeouts
NAME_BID_TIMEOUTS = {
    13: 0,
    8: 1 * NAME_BID_TIMEOUT_BLOCKS,  # 480 blocks
    4: 31 * NAME_BID_TIMEOUT_BLOCKS,  # 14880 blocks
    1: 62 * NAME_BID_TIMEOUT_BLOCKS,  # 29760 blocks
}

# dry run
DRY_RUN_ADDRESS = "ak_11111111111111111111111111111111273Yts"
DRY_RUN_AMOUNT = 100000000000000000000000000000000000
