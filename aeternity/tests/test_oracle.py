import logging
import pytest

from aeternity.tests import EPOCH_CLI
from aeternity.oracle import Oracle, OracleQuery

logger = logging.getLogger(__name__)
# to run this test in other environments set the env vars as specified in the
# config.py

logging.basicConfig(level=logging.DEBUG)


class WeatherOracle(Oracle):
    def get_response(self, message):
        query = message['payload']['query']
        logger.debug('Received query %s' % query)
        response = "{'temp_c': 30}"  # nice and sunny
        logger.debug('Sending back %s' % str(response))
        return response


class WeatherQuery(OracleQuery):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_received = False  # for testing, record if we received anything

    def on_response(self, response, query):
        logger.debug('Weather Oracle Received a response! %s' % response)
        self.response_received = True


@pytest.mark.skip('skip tests for v0.13.0')
def test_oracle_registration():
    weather_oracle = WeatherOracle(
        query_format="{'city': str}",
        response_format="{'temp_c': int}",
        default_query_fee=0,
        default_fee=10,
        default_ttl=50,
        default_query_ttl=2,
        default_response_ttl=2,
    )
    EPOCH_CLI.register_oracle(weather_oracle)
    EPOCH_CLI.listen_until(weather_oracle.is_ready, timeout=5)
    assert weather_oracle.oracle_id is not None


@pytest.mark.skip('skip tests for v0.13.0')
def test_oracle_query_received():
    weather_oracle = WeatherOracle(
        query_format="{'city': str}",
        response_format="{'temp_c': int}",
        default_query_fee=0,
        default_fee=10,
        default_ttl=50,
        default_query_ttl=2,
        default_response_ttl=2,
    )
    EPOCH_CLI.register_oracle(weather_oracle)
    EPOCH_CLI.listen_until(weather_oracle.is_ready, timeout=5)
    weather_query = WeatherQuery(
        oracle_pubkey=weather_oracle.oracle_id,
        query_fee=0,
        fee=10,
        query_ttl=2,
        response_ttl=2,
    )
    EPOCH_CLI.mount(weather_query)
    weather_query.query("{'city': 'Berlin'}")
    EPOCH_CLI.listen_until(lambda: weather_query.response_received, timeout=5)
