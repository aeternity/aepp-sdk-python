# API identifiers
# https://github.com/aeternity/protocol/blob/14db60b7db4d51618ebad539aaf6a0b40b72e633/epoch/api/api_encoding.md#encoding-scheme-for-api-identifiers-and-byte-arrays

# base58
ACCOUNT_PUBKEY = "ak"  # base58	Account pubkey
BLOCK_PROOF_OF_FRAUD_HASH = "bf"  # base58	Block Proof of Fraud hash
BLOCK_STATE_HASH = "bs"  # base58	Block State hash
BLOCK_TRANSACTION_HASH = "bx"  # base58	Block transaction hash
CHANNEL = "ch"  # base58	Channel
COMMITMENT = "cm"  # base58	Commitment
CONTRACT_PUBKEY = "ct"  # base58	Contract pubkey
KEY_BLOCK_HASH = "kh"  # base58	Key block hash
MICRO_BLOCK_HASH = "mh"  # base58	Micro block hash
NAME = "nm"  # base58	Name
ORACLE_PUBKEY = "ok"  # base58	Oracle pubkey
ORACLE_QUERY_ID = "oq"  # base58	Oracle query id
PEER_PUBKEY = "pp"  # base58	Peer pubkey
SIGNATURE = "sg"  # base58	Signature
TRANSACTION_HASH = "th"  # base58	Transaction hash

# Base 64
CONTRACT_BYTE_ARRAY = "cb"  # base64	Contract byte array
ORACLE_RESPONSE = "or"  # base64	Oracle response
ORACLE_QUERY = "ov"  # base64	Oracle query
PROOF_OF_INCLUSION = "pi"  # base64	Proof of Inclusion
STATE_TREES = "ss"  # base64	State trees
STATE = "st"  # base64	State
TRANSACTION = "tx"  # base64	Transaction

IDENTIFIERS_B58 = set([
    ACCOUNT_PUBKEY,
    BLOCK_PROOF_OF_FRAUD_HASH,
    BLOCK_STATE_HASH,
    BLOCK_TRANSACTION_HASH,
    CHANNEL,
    COMMITMENT,
    CONTRACT_PUBKEY,
    KEY_BLOCK_HASH,
    MICRO_BLOCK_HASH,
    NAME,
    ORACLE_PUBKEY,
    ORACLE_QUERY_ID,
    PEER_PUBKEY,
    SIGNATURE,
    TRANSACTION_HASH,
])

# Indentifiers with base64
IDENTIFIERS_B64 = set([
    CONTRACT_BYTE_ARRAY,
    ORACLE_RESPONSE,
    ORACLE_QUERY,
    PROOF_OF_INCLUSION,
    STATE_TREES,
    STATE,
    TRANSACTION
])
