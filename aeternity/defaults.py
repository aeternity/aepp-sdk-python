from aeternity import identifiers

# fee calculation
BASE_GAS = 15000
GAS_PER_BYTE = 20
GAS_PRICE = 1000000000
# max number of block into the future that the name is going to be available
# https://github.com/aeternity/protocol/blob/epoch-v0.22.0/AENS.md#update
# https://github.com/aeternity/protocol/blob/44a93d3aab957ca820183c3520b9daf6b0fedff4/AENS.md#aens-entry
MAX_NAME_TLL = 36000
MAX_NAME_CLIENT_TTL = 60000
NAME_TTL = 500
# default relative ttl in number of blocks  for executing transaction on the chain
MAX_TX_TTL = 256
TX_TTL = 0
# contracts
CONTRACT_GAS = 1000000000
CONTRACT_GAS_PRICE = 1000000000
CONTRACT_DEPOSIT = 0
CONTRACT_AMOUNT = 0
# oracles
# https://github.com/aeternity/protocol/blob/master/oracles/oracles.md#technical-aspects-of-oracle-operations
ORACLE_VM_VERSION = identifiers.NO_VM
ORACLE_QUERY_FEE = 0
ORACLE_TTL_VALUE = 500
ORACLE_QUERY_TTL_VALUE = 10
ORACLE_RESPONSE_TTL_VALUE = 10
KEY_BLOCK_INTERVAL = 3
# network id
NETWORK_ID = identifiers.NETWORK_ID_MAINNET
# TUNING
MAX_RETRIES = 8  # used in exponential backoff when checking a transaction
POLLING_INTERVAL = 2  # in seconds
