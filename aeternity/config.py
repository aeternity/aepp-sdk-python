import os

import requests


class ConfigException(Exception):
    pass

class Config:
    default_config = None

    def __init__(self, local_port=None, internal_port=None, websocket_port=None, host='localhost'):
        try:
            if local_port is None:
                local_port = os.environ.get('AE_LOCAL_PORT', 3013)
            self.local_port = local_port
            if internal_port is None:
                internal_port = os.environ.get('AE_LOCAL_INTERNAL_PORT', 3113)
            self.local_internal_port = internal_port
            if websocket_port is None:
                websocket_port = os.environ.get('AE_WEBSOCKET', 3114)
            self.websocket_port = websocket_port
        except KeyError:
            raise ConfigException(
                'You must either specify the Config manually, use '
                'Config.set_default or provide the env vars AE_LOCAL_PORT, '
                'AE_LOCAL_INTERNAL_PORT and AE_WEBSOCKET'
            )

        self.websocket_url = f'ws://{host}:{self.websocket_port}/websocket'
        self.http_api_url = f'http://{host}:{self.local_port}/v2'
        self.internal_api_url = f'http://{host}:{self.local_internal_port}/v2'

        self.name_url = f'{self.http_api_url}/name'
        self.pre_claim_url = self.internal_api_url + "/name-preclaim-tx"
        self.claim_url = self.internal_api_url + "/name-claim-tx"
        self.update_url = self.internal_api_url + "/name-update-tx"
        self.transfer_url = self.internal_api_url + "/name-transfer-tx"
        self.revoke_url = self.internal_api_url + "/name-revoke-tx"

        self.pubkey = None

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
    def set_default(cls, config):
        """
        sets the default configuration that will be used when the epoch client
        did not get a config passed into its constructor

        :return: None
        """
        cls.default_config = config

    @classmethod
    def get_default(cls):
        """
        returns the previously set default config or constructs a configuration
        automatically from environment variables

        :return: Config
        """
        if cls.default_config is None:
            cls.default_config = Config()
        return cls.default_config
