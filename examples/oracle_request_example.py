#!/usr/env/bin python
import logging

from aeternity.config import Config
from aeternity.oracle import EpochClient
from aeternity.oracle import Oracle


logging.basicConfig(level=logging.DEBUG)

dev1_config = Config(local_port=3013, internal_port=3113, websocket_port=3114)
dev2_config = Config(local_port=3023, internal_port=3123, websocket_port=3124)
client = EpochClient(config=dev1_config)

oracle_id = 'ok$3ZTGFF2EyRGBVRsJhUs2CuRUqGXW1AthNWKAQTFDmhcHwDfEWtqR4QXbFoEGc96Kf6edoqmh6stPYbdt7stPSKp34E3GZC'



client.ask_oracle(
    oracle_pub_key=oracle_id,
    query_fee=4,
    query_ttl=10,
    response_ttl=10,
    fee=6,
    query="what the current the temperature?"
)
client.run()
