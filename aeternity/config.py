import os

import requests
from collections import MutableSequence


class ConfigException(Exception):
    pass


ae_default_external_host = 'localhost'
ae_default_external_port = 3013
ae_default_internal_host = 'localhost'
ae_default_internal_port = 3113
ae_default_websocket_host = 'localhost'
ae_default_websocket_port = 3114

class Config:
    default_configs = None

    def __init__(self, external_host=None, internal_host=None, websocket_host=None):
        try:
            if external_host is None:
                host = os.environ.get('AE_EXTERNAL_HOST', ae_default_external_host)
                port = os.environ.get('AE_EXTERNAL_PORT', ae_default_external_port)
                external_host = f'{host}:{port}'
            self.external_host_port = external_host
            if internal_host is None:
                host = os.environ.get('AE_INTERNAL_HOST', ae_default_internal_host)
                port = os.environ.get('AE_INTERNAL_PORT', ae_default_internal_port)
                internal_host = f'{host}:{port}'
            self.internal_host_port = internal_host
            if websocket_host is None:
                host = os.environ.get('AE_WEBSOCKET_HOST', ae_default_websocket_host)
                port = os.environ.get('AE_WEBSOCKET_PORT', ae_default_websocket_port)
                websocket_host = f'{host}:{port}'
            self.websocket_host_port = websocket_host
        except KeyError:
            raise ConfigException(
                'You must either specify the Config manually, use '
                'Config.set_default or provide the env vars'
                'AE_EXTERNAL_HOST, AE_EXTERNAL_PORT, '
                'AE_INTERNAL_HOST, AE_INTERNAL_PORT, '
                'AE_WEBSOCKET_HOST and AE_WEBSOCKET_PORT'

            )

        self.websocket_url = f'ws://{self.websocket_host_port}/websocket'
        self.http_api_url = f'http://{self.external_host_port}/v2'
        self.internal_api_url = f'http://{self.internal_host_port}/v2'

        self.name_url = f'{self.http_api_url}/name'
        self.pubkey = None

    def __str__(self):
        ws = self.websocket_host_port
        external = self.external_host_port
        internal = self.internal_host_port
        return f'ws:{ws} ext:{external} int:{internal}'

    @property
    def top_block_url(self):
        return f'{self.http_api_url}/top'

    @property
    def pubkey_url(self):
        return f'{self.internal_api_url}/account/pub-key'

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
