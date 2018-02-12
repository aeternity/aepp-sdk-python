#!/usr/env/bin python
import logging

from aeternity.config import Config
from aeternity.oracle import EpochClient
from aeternity.oracle import Oracle


logging.basicConfig(level=logging.DEBUG)


class WeatherOracle(Oracle):
    query_format = 'weather_query2'
    response_format = 'weather_resp2'
    default_query_fee = 4
    default_fee = 6
    default_query_ttl = 10
    default_response_ttl = 10

    def get_reply(self, message):
        return '26 C'


dev1_config = Config(local_port=3013, internal_port=3113, websocket_port=3114)

weather_oracle = WeatherOracle()
client = EpochClient(config=dev1_config)
client.register_oracle(weather_oracle)
print(f'''You can now query this oracle using the following parameters:
    oracle_pub_key: {client.get_pub_key()}
    query_fee: {weather_oracle.get_query_fee()}
    query_ttl: {weather_oracle.get_query_ttl()}
    response_ttl: {weather_oracle.get_response_ttl()}
    fee: {weather_oracle.get_fee()}
    query_format: {weather_oracle.query_format}
''')
print('Oracle ready')
client.run()
print('Oracle Stopped')
