import logging
import os
from urllib.parse import urlparse
from aeternity.config import Config

logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)


PUBLIC_KEY = os.environ.get('WALLET_PUB')
PRIVATE_KEY = os.environ.get('WALLET_PRIV')
NODE_URL = os.environ.get('TEST_URL')

o = urlparse(NODE_URL)
secured = True if o.scheme == 'https' else False

Config.set_defaults(Config(
    external_host=f"{o.hostname}:{o.port}",
    internal_host=f'{o.hostname}:{o.port}/internal',
    secure_connection=secured
))
