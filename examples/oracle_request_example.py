#!/usr/bin/env python
import json
import logging
import sys
import os

# this is just a hack to get this example to import a parent folder:
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..')))

from aeternity import Config
from aeternity import EpochClient
from aeternity import OracleQuery

logging.basicConfig(level=logging.DEBUG)

class AeternityInUSDOracleQuery(OracleQuery):
    def on_response(self, message, query):
        print(query)
        print(message)


dev1_config = Config(external_host=3013, internal_host=3113, websocket_host=3114)
client = EpochClient(configs=dev1_config)
oracle_pubkey = 'ok$3WRqCYwdr9B5aeAMT7Bfv2gGZpLUdD4RQM4hzFRpRzRRZx7d8pohQ6xviXxDTLHVwWKDbGzxH1xRp19LtwBypFpCVBDjEQ'

oracle_query = AeternityInUSDOracleQuery(
    oracle_pubkey=oracle_pubkey,
    query_fee=4,
    query_ttl=10,
    response_ttl=10,
    fee=6,
)
client.mount(oracle_query)
oracle_query.query(json.dumps({
    'url': 'https://api.coinmarketcap.com/v1/ticker/aeternity/?convert=USD',
    'jq': '.[0].price_usd',
}))
client.listen()
