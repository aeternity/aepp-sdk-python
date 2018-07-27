

import requests
import sys
from collections import MutableSequence


# max number of block into the future that the name is going to be available
# https://github.com/aeternity/protocol/blob/epoch-v0.13.0/AENS.md#update
# https://github.com/aeternity/protocol/blob/44a93d3aab957ca820183c3520b9daf6b0fedff4/AENS.md#aens-entry
NAME_MAX_TLL = 50000
NAME_DEFAULT_TTL = 60000
# default relative ttl in number of blocks  for executing transaction on the chain
MAX_TX_TTL = sys.maxsize
DEFAULT_TX_TTL = 10
# default fee for posting transacrtion
DEFAULT_FEE = 1
# contracts
CONTRACT_DEFAULT_GAS = 40000000
CONTRACT_DEFAULT_GAS_PRICE = 1
CONTRACT_DEFAULT_DEPOSIT = 4
CONTRACT_DEFAULT_VM_VERSION = 1

# params
# can be message_pack or json
PARAM_DEFAULT_ENCODING = 'json'


class ConfigException(Exception):
    pass


class Config:
    default_configs = None

    def __init__(self,
                 external_url='http://localhost:3013',
                 internal_url='http://localhost:3113',
                 websocket_url=None):

        # enpoint urls
        self.websocket_url = websocket_url
        self.api_url_internal = internal_url
        self.api_url = external_url
        # get the version
        self.name_url = f'{self.api_url}/name'
        self.pubkey = None
        # retrieve the version of the node we are connecting to
        try:
            r = requests.get(f"{self.api_url}/v2/version").json()
            self.node_version = r['version']
        except requests.exceptions.ConnectionError as e:
            raise ConfigException(f"Error connecting to the epoch node at {self.api_url}, connection unavailable")

    def __str__(self):
        return f'ws:{self.websocket_url} ext:{self.api_url} int:{self.api_url_internal}'

    @property
    def top_block_url(self):
        return f'{self.api_url}/top'

    @property
    def pubkey_url(self):
        return f'{self.api_url_internal}/account/pub-key'

    def get_pubkey(self):
        if self.pubkey is None:
            self.pubkey = requests.get(self.pubkey_url).json()['pub_key']
        return self.pubkey

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
