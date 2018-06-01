

import requests
from collections import MutableSequence


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
        r = requests.get(f"{self.api_url}/v2/version").json()
        self.node_version = r['version']

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
