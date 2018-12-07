import sys
from collections import MutableSequence

# vm version specification
# https://github.com/aeternity/protocol/blob/master/contracts/contract_vms.md#virtual-machines-on-the-%C3%A6ternity-blockchain
AEVM_NO_VM = 0
# fee calculation
GAS_PER_BYTE = 20
BASE_GAS = 15000
# max number of block into the future that the name is going to be available
# https://github.com/aeternity/protocol/blob/epoch-v0.22.0/AENS.md#update
# https://github.com/aeternity/protocol/blob/44a93d3aab957ca820183c3520b9daf6b0fedff4/AENS.md#aens-entry
NAME_MAX_TLL = 36000
NAME_CLIENT_TTL = 60000
DEFAULT_NAME_TTL = 500
# default relative ttl in number of blocks  for executing transaction on the chain
MAX_TX_TTL = sys.maxsize
DEFAULT_TX_TTL = 0
# default fee for posting transaction
DEFAULT_FEE = 20000
# contracts
CONTRACT_DEFAULT_GAS = 170000
CONTRACT_DEFAULT_GAS_PRICE = 1
CONTRACT_DEFAULT_DEPOSIT = 4
CONTRACT_DEFAULT_VM_VERSION = 1
CONTRACT_DEFAULT_AMOUNT = 1
# oracles
# https://github.com/aeternity/protocol/blob/master/oracles/oracles.md#technical-aspects-of-oracle-operations
ORACLE_DEFAULT_QUERY_FEE = 30000
ORACLE_DEFAULT_TTL_TYPE_DELTA = 'delta'
ORACLE_DEFAULT_TTL_TYPE_BLOCK = 'block'
ORACLE_DEFAULT_TTL_VALUE = 500
ORACLE_DEFAULT_QUERY_TTL_VALUE = 10
ORACLE_DEFAULT_RESPONSE_TTL_VALUE = 10
ORACLE_DEFAULT_VM_VERSION = AEVM_NO_VM


# network id
DEFAULT_NETWORK_ID = "ae_mainnet"
# TUNING
MAX_RETRIES = 8  # used in exponential backoff when checking a transaction
POLLING_INTERVAL = 2  # in seconds


class Config:
    default_configs = None

    def __init__(self,
                 external_url='http://localhost:3013',
                 internal_url='http://localhost:3113',
                 channels_url='http://localhost:3014',
                 network_id=DEFAULT_NETWORK_ID):

        # endpoint urls
        self.channels_url = channels_url
        self.api_url_internal = internal_url
        self.api_url = external_url
        self.network_id = network_id

    def __str__(self):
        return f'ext:{self.api_url} int:{self.api_url_internal} ch:{self.channels_url} '

    @classmethod
    def set_defaults(cls, config):
        """
        sets the default configuration that will be used when the epoch client
        did not get a config passed into its constructor

        :return: None
        """
        if not isinstance(config, MutableSequence):
            config = [config]
        cls.default_configs = config

    @classmethod
    def get_defaults(cls):
        """
        returns the previously set default config or constructs a configuration
        automatically from environment variables

        :return: Config
        """
        if cls.default_configs is None:
            cls.default_configs = [Config()]
        return cls.default_configs
