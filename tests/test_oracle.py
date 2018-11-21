import logging
import pytest

from tests import EPOCH_CLI, ACCOUNT, ACCOUNT_1
from aeternity.oracles import Oracle, OracleQuery

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


def _test_oracle_registration(account):
    oracle = EPOCH_CLI.Oracle()
    weather_oracle = dict(
        account=account,
        query_format="{'city': str}",
        response_format="{'temp_c': int}",
    )
    tx, tx_signed, signature, tx_hash = oracle.register(**weather_oracle)
    assert oracle.id == account.get_address().replace("ak_", "ok_")
    oracle_api_response = EPOCH_CLI.get_oracle_by_pubkey(pubkey=oracle.id)
    assert oracle_api_response.id == oracle.id
    return oracle


def _test_oracle_query(oracle, sender, query):
    tx, tx_signed, signature, tx_hash = oracle.query(sender, query)
    print(tx)


def test_oracle_lifecycle_debug():
    # registration
    EPOCH_CLI.set_native(False)
    oracle = _test_oracle_registration(ACCOUNT)
    # query
    _test_oracle_query(oracle, ACCOUNT_1, "{'city': 'Berlin'}")


@pytest.mark.skip('skip tests for v0.13.0')
def test_oracle_lifecycle_native():
    # registration
    EPOCH_CLI.set_native(True)
    oracle = _test_oracle_registration(ACCOUNT_1)
    # query
    _test_oracle_query(oracle, ACCOUNT, "{'city': 'Sofia'}")


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
