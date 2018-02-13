import random
import string

import logging
logger = logging.getLogger(__name__)

from aeternity import Config, EpochClient, Oracle, OracleQuery
from aeternity.aens import AEName, AENSException
from aeternity.config import ConfigException

# to run this test in other environments set the env vars as specified in the
# config.py
try:
    # if there are no env vars set for the config, this call will fail
    Config()
except ConfigException:
    # in this case we create a default config that should work on the dev
    # machines.
    Config.set_default(Config(local_port=3013, internal_port=3113, websocket_port=3114))


logging.basicConfig(level=logging.DEBUG)


class WeatherOracle(Oracle):
    def get_response(self, message):
        query = message['payload']['query']
        logger.debug('Received query %s' % query)
        response = "{'temp_c': 30}"  # nice and sunny
        logger.debug('Sending back %s' % str(response))
        return response


class WeatherQuery(OracleQuery):
    oracle_pubkey = None
    query_fee = 0
    fee = 10
    query_ttl = 2
    response_ttl = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_received = False

    def on_response(self, response, query):
        print('Weather Oracle Received a response! %s' % response)
        self.response_received = True



def test_oracle_registration():
    client = EpochClient()
    weather_oracle = WeatherOracle(
        query_format="{'city': str}",
        response_format= "{'temp_c': int}",
        default_query_fee=0,
        default_fee=10,
        default_ttl=50,
        default_query_ttl=2,
        default_response_ttl=2,
    )
    client.register_oracle(weather_oracle)
    client.consume_until(weather_oracle.is_ready, timeout=40)
    assert weather_oracle.oracle_id is not None

def test_oracle_query_received():
    client = EpochClient()
    weather_oracle = WeatherOracle(
        query_format="{'city': str}",
        response_format="{'temp_c': int}",
        default_query_fee=0,
        default_fee=10,
        default_ttl=50,
        default_query_ttl=2,
        default_response_ttl=2,
    )
    client.register_oracle(weather_oracle)
    client.consume_until(weather_oracle.is_ready, timeout=180)
    weather_query = WeatherQuery(oracle_pubkey=weather_oracle.oracle_id)
    client.mount(weather_query)
    client._tick()
    weather_query.query("{'city': 'Berlin'}")
    client.consume_until(lambda: weather_query.response_received, timeout=180)
