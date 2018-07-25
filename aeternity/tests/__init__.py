import logging
import os
from aeternity.config import Config
from aeternity.signing import KeyPair

logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)


PUBLIC_KEY = os.environ.get('WALLET_PUB')
PRIVATE_KEY = os.environ.get('WALLET_PRIV')
NODE_URL = os.environ.get('TEST_URL')
NODE_URL_INTERNAL = os.environ.get('TEST_INTERNAL_URL')
EPOCH_VERSION = '0.18.0'
# set the key folder as environment variables
KEYPAIR = KeyPair.from_public_private_key_strings(PUBLIC_KEY, PRIVATE_KEY)


Config.set_defaults(Config(
    external_url=NODE_URL,
    internal_url=NODE_URL_INTERNAL
))
