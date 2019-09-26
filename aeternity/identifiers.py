# API identifiers
# https://github.com/aeternity/protocol/blob/14db60b7db4d51618ebad539aaf6a0b40b72e633/epoch/api/api_encoding.md#encoding-scheme-for-api-identifiers-and-byte-arrays

# base58
ACCOUNT_ID = "ak"  # base58	Account pubkey
BLOCK_PROOF_OF_FRAUD_HASH = "bf"  # base58	Block Proof of Fraud hash
BLOCK_STATE_HASH = "bs"  # base58	Block State hash
BLOCK_TRANSACTION_HASH = "bx"  # base58	Block transaction hash
CHANNEL = "ch"  # base58	Channel
COMMITMENT = "cm"  # base58	Commitment
CONTRACT_ID = "ct"  # base58	Contract pubkey
KEY_BLOCK_HASH = "kh"  # base58	Key block hash
MICRO_BLOCK_HASH = "mh"  # base58	Micro block hash
NAME = "nm"  # base58	Name
ORACLE_ID = "ok"  # base58	Oracle pubkey
ORACLE_QUERY_ID = "oq"  # base58	Oracle query id
PEER_ID = "pp"  # base58	Peer pubkey
SIGNATURE = "sg"  # base58	Signature
TRANSACTION_HASH = "th"  # base58	Transaction hash

# Base 64
BYTECODE = "cb"  # base64	Contract byte array
ORACLE_RESPONSE = "or"  # base64	Oracle response
ORACLE_QUERY = "ov"  # base64	Oracle query
PROOF_OF_INCLUSION = "pi"  # base64	Proof of Inclusion
STATE_TREES = "ss"  # base64	State trees
STATE = "st"  # base64	State
TRANSACTION = "tx"  # base64	Transaction
BYTE_ARRAY = "ba"  # base64 byte array

IDENTIFIERS_B58 = set([
    ACCOUNT_ID,
    BLOCK_PROOF_OF_FRAUD_HASH,
    BLOCK_STATE_HASH,
    BLOCK_TRANSACTION_HASH,
    CHANNEL,
    COMMITMENT,
    CONTRACT_ID,
    KEY_BLOCK_HASH,
    MICRO_BLOCK_HASH,
    NAME,
    ORACLE_ID,
    ORACLE_QUERY_ID,
    PEER_ID,
    SIGNATURE,
    TRANSACTION_HASH,
])

# Identifiers with base64
IDENTIFIERS_B64 = set([
    BYTECODE,
    ORACLE_RESPONSE,
    ORACLE_QUERY,
    PROOF_OF_INCLUSION,
    STATE_TREES,
    STATE,
    TRANSACTION,
    BYTE_ARRAY
])

# Account address encoding formats
ACCOUNT_API_FORMAT = 'api'
ACCOUNT_SOFIA_FORMAT = 'sofia'
ACCOUNT_RAW_FORMAT = 'raw'

# RLP Identifiers

# RLP version number
# https://github.com/aeternity/protocol/blob/api-v0.10.1/serializations.md#binary-serialization
VSN = 1

# Tag constant for ids (type uint8)
# see https://github.com/aeternity/protocol/blob/master/serializations.md#the-id-type
# <<Tag:1/unsigned-integer-unit:8, Hash:32/binary-unit:8>>
ID_TAG_ACCOUNT = 1
ID_TAG_NAME = 2
ID_TAG_COMMITMENT = 3
ID_TAG_ORACLE = 4
ID_TAG_CONTRACT = 5
ID_TAG_CHANNEL = 6

# Maps numeric tags to string prefixes
ID_TAG_TO_PREFIX = {
    ID_TAG_ACCOUNT: ACCOUNT_ID,
    ID_TAG_CHANNEL: CHANNEL,
    ID_TAG_COMMITMENT: COMMITMENT,
    ID_TAG_CONTRACT: CONTRACT_ID,
    ID_TAG_NAME: NAME,
    ID_TAG_ORACLE: ORACLE_ID
}

# Maps string prefixes to numeric tags
ID_PREFIX_TO_TAG = {
    ACCOUNT_ID: ID_TAG_ACCOUNT,
    CHANNEL: ID_TAG_CHANNEL,
    COMMITMENT: ID_TAG_COMMITMENT,
    CONTRACT_ID: ID_TAG_CONTRACT,
    NAME: ID_TAG_NAME,
    ORACLE_ID: ID_TAG_ORACLE
}

# Object tags
# see https://github.com/aeternity/protocol/blob/master/serializations.md#binary-serialization

OBJECT_TAG_ACCOUNT = 10
OBJECT_TAG_SIGNED_TRANSACTION = 11
OBJECT_TAG_SPEND_TRANSACTION = 12
OBJECT_TAG_ORACLE = 20
OBJECT_TAG_ORACLE_QUERY = 21
OBJECT_TAG_ORACLE_REGISTER_TRANSACTION = 22
OBJECT_TAG_ORACLE_QUERY_TRANSACTION = 23
OBJECT_TAG_ORACLE_RESPONSE_TRANSACTION = 24
OBJECT_TAG_ORACLE_EXTEND_TRANSACTION = 25
OBJECT_TAG_NAME_SERVICE_NAME = 30
OBJECT_TAG_NAME_SERVICE_COMMITMENT = 31
OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION = 32
OBJECT_TAG_NAME_SERVICE_PRECLAIM_TRANSACTION = 33
OBJECT_TAG_NAME_SERVICE_UPDATE_TRANSACTION = 34
OBJECT_TAG_NAME_SERVICE_REVOKE_TRANSACTION = 35
OBJECT_TAG_NAME_SERVICE_TRANSFER_TRANSACTION = 36
OBJECT_TAG_CONTRACT = 40
OBJECT_TAG_CONTRACT_CALL = 41
OBJECT_TAG_CONTRACT_CREATE_TRANSACTION = 42
OBJECT_TAG_CONTRACT_CALL_TRANSACTION = 43
OBJECT_TAG_SOPHIA_BYTE_CODE = 70
OBJECT_TAG_CHANNEL_CREATE_TRANSACTION = 50
OBJECT_TAG_CHANNEL_DEPOSIT_TRANSACTION = 51
OBJECT_TAG_CHANNEL_WITHDRAW_TRANSACTION = 52
OBJECT_TAG_CHANNEL_FORCE_PROGRESS_TRANSACTION = 521
OBJECT_TAG_CHANNEL_CLOSE_MUTUAL_TRANSACTION = 53
OBJECT_TAG_CHANNEL_CLOSE_SOLO_TRANSACTION = 54
OBJECT_TAG_CHANNEL_SLASH_TRANSACTION = 55
OBJECT_TAG_CHANNEL_SETTLE_TRANSACTION = 56
OBJECT_TAG_CHANNEL_OFF_CHAIN_TRANSACTION = 57
OBJECT_TAG_CHANNEL_OFF_CHAIN_UPDATE_TRANSFER = 570
OBJECT_TAG_CHANNEL_OFF_CHAIN_UPDATE_DEPOSIT = 571
OBJECT_TAG_CHANNEL_OFF_CHAIN_UPDATE_WITHDRAWAL = 572
OBJECT_TAG_CHANNEL_OFF_CHAIN_UPDATE_CREATE_CONTRACT = 573
OBJECT_TAG_CHANNEL_OFF_CHAIN_UPDATE_CALL_CONTRACT = 574
OBJECT_TAG_CHANNEL = 58
OBJECT_TAG_CHANNEL_SNAPSHOT_TRANSACTION = 59
OBJECT_TAG_POI = 60
OBJECT_TAG_MICRO_BODY = 101
OBJECT_TAG_LIGHT_MICRO_BLOCK = 102
OBJECT_TAG_GA_ATTACH_TRANSACTION = 80
OBJECT_TAG_GA_META_TRANSACTION = 81


# VM Identifiers
# vm version specification
# https://github.com/aeternity/protocol/blob/master/contracts/contract_vms.md#virtual-machines-on-the-%C3%A6ternity-blockchain
NO_VM = 0
VM_SOPHIA = 1
VM_SOLIDITY = 2
VM_SOPHIA_IMPROVEMENTS = 3
# abi
NO_ABI = 0
ABI_SOPHIA = 1
ABI_SOLIDITY = 2
# Consensus Protocol
PROTOCOL_ROMA = 1
PROTOCOL_MINERVA = 2
PROTOCOL_FORTUNA = 3
PROTOCOL_LIMA = 4
# Contracts identifiers
PROTOCOL_ABI_VM = {
    PROTOCOL_ROMA: {
        "vm": 0,  # this is to maintain retro-compatibility
        "abi": 1
    },
    PROTOCOL_MINERVA: {
        # For Minerva: 196609  # that is int.from_bytes(int(3).to_bytes(2, "big") + int(1).to_bytes(2, "big"), "big")
        "vm": 3,
        "abi": 1
    },
    PROTOCOL_FORTUNA: {
        "vm": 4,
        "abi": 1
    },
    PROTOCOL_LIMA: {
        "vm": 5,
        "abi": 1
    }
}


# Oracles
ORACLE_TTL_TYPE_DELTA = 'delta'
ORACLE_TTL_TYPE_BLOCK = 'block'

# Network IDS
NETWORK_ID_MAINNET = "ae_mainnet"
NETWORK_ID_TESTNET = "ae_uat"

# Accounts Kind
ACCOUNT_KIND_BASIC = "basic"
ACCOUNT_KIND_GENERALIZED = "generalized"
