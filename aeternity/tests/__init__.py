import logging
from aeternity import Config

logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

KEY_PATH = '/Users/andrea/Documents/workspaces/blockchain/aeternity/epoch/deployment/ansible/files/tester'
KEY_PASSWORD = 'secret'


Config.set_defaults(Config(
    external_host='sdk-testnet.aepps.com:443',
    internal_host='sdk-testnet.aepps.com:443/internal',
    secure_connection=True
))
