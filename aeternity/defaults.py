from aeternity import identifiers

# fee calculation
BASE_GAS = 15000
GAS_PER_BYTE = 20
GAS_PRICE = 1000000000
# max number of block into the future that the name is going to be available
# https://github.com/aeternity/protocol/blob/epoch-v0.22.0/AENS.md#update
# https://github.com/aeternity/protocol/blob/44a93d3aab957ca820183c3520b9daf6b0fedff4/AENS.md#aens-entry
NAME_MAX_TLL = 36000
NAME_MAX_CLIENT_TTL = 84600
NAME_CLIENT_TTL = NAME_MAX_CLIENT_TTL
NAME_TTL = 500
# default relative ttl in number of blocks  for executing transaction on the chain
MAX_TX_TTL = 256
TX_TTL = 0
FEE = 0
# contracts
CONTRACT_GAS = 1000000000
CONTRACT_GAS_PRICE = 1000000000
CONTRACT_DEPOSIT = 0
CONTRACT_AMOUNT = 0
# calldata for the init function with no parameters
CONTRACT_INIT_CALLDATA = "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACC5yVbyizFJqfWYeqUF89obIgnMVzkjQAYrtsG9n5" + \
    "+Z6gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnHQYrA=="
# oracles
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
