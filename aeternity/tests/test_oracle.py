import random
import string

import logging
from pytest import raises

from aeternity import Config, EpochClient, Oracle
from aeternity.aens import InvalidName, Name, AENSException
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


class FakeWeatherOracle(Oracle):
    query_format = "{'city': str}"
    response_format = "{'temp_c': int}"
    default_query_fee = 0
    default_fee = 6
    default_query_ttl = 10
    default_response_ttl = 10

    def get_response(self, message):
        print('Received %s' % str(message))
        return "{'temp_c': 30}"  # nice and sunny


def test_oracle_registration():
    client = EpochClient()
    weather_oracle = FakeWeatherOracle()
    client.register_oracle(weather_oracle)
    assert weather_oracle.oracle_id is not None

