import logging
import os
from urllib.parse import urlparse
from aeternity.config import Config

logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)


PUBLIC_KEY = os.environ.get('WALLET_PUB')
PRIVATE_KEY = os.environ.get('WALLET_PRIV')
NODE_URL = os.environ.get('TEST_URL')
NODE_URL_INTERNAL = os.environ.get('TEST_INTERNAL_URL')

# external node
node = urlparse(NODE_URL)
secured = True if node.scheme == 'https' else False
external_host = f"{node.hostname}:{node.port}"
# internal node
node = urlparse(NODE_URL_INTERNAL)
secured = True if node.scheme == 'https' else False
internal_host = f"{node.hostname}:{node.port}"

Config.set_defaults(Config(
    external_host=external_host,
    internal_host=internal_host,
    secure_connection=secured
))
