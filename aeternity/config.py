import requests
import sys
from collections import MutableSequence
from . import __compatibility__


# max number of block into the future that the name is going to be available
# https://github.com/aeternity/protocol/blob/epoch-v0.22.0/AENS.md#update
# https://github.com/aeternity/protocol/blob/44a93d3aab957ca820183c3520b9daf6b0fedff4/AENS.md#aens-entry
NAME_MAX_TLL = 36000
NAME_CLIENT_TTL = 60000
DEFAULT_NAME_TTL = 500
# default relative ttl in number of blocks  for executing transaction on the chain
MAX_TX_TTL = sys.maxsize
DEFAULT_TX_TTL = 500
# default fee for posting transaction
DEFAULT_FEE = 1
# contracts
CONTRACT_DEFAULT_GAS = 1000
CONTRACT_DEFAULT_GAS_PRICE = 1
CONTRACT_DEFAULT_DEPOSIT = 4
CONTRACT_DEFAULT_VM_VERSION = 1
# TUNING
MAX_RETRIES = 7  # used in exponential backoff when checking a transaction
POLLING_INTERVAL = 2  # in seconds


class ConfigException(Exception):
    pass


class UnsupportedEpochVersion(Exception):
    pass


class Config:
    default_configs = None

    def __init__(self,
                 external_url='http://localhost:3013',
                 internal_url='http://localhost:3113',
                 websocket_url=None,
                 force_compatibility=False):

        # endpoint urls
        self.websocket_url = websocket_url
        self.api_url_internal = internal_url
        self.api_url = external_url
        # get the version
        self.name_url = f'{self.api_url}/name'
        self.pubkey = None
        # retrieve the version of the node we are connecting to
        try:
            r = requests.get(f"{self.api_url}/v2/status").json()
            self.node_version = r.get('node_version', 'unknown')
            if self.node_version not in __compatibility__ and not force_compatibility:
                raise UnsupportedEpochVersion(f"Unsupported epoch version {self.node_version}, supported version are {', '.join(__compatibility__)}")
        except requests.exceptions.ConnectionError as e:
            raise ConfigException(f"Error connecting to the epoch node at {self.api_url}, connection unavailable")
        except Exception as e:
            raise UnsupportedEpochVersion(f"Unable to understand node reply, perhaps is not an epoch node or is too old?")

    def __str__(self):
        return f'ws:{self.websocket_url} ext:{self.api_url} int:{self.api_url_internal}'

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
