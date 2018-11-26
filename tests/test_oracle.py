import logging
import pytest

from tests import EPOCH_CLI, ACCOUNT, ACCOUNT_1
from aeternity.oracles import Oracle, OracleQuery
from aeternity import hashing

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
    q = EPOCH_CLI.OracleQuery(oracle.id)
    q.execute(sender, query)
    return q


def _test_oracle_respond(oracle, query, account, response):
    tx, tx_signed, signature, tx_hash = oracle.respond(account, query.id, response)


def _test_oracle_response(query, expected):
    r = query.get_response_object()
    assert r.oracle_id == query.oracle_id
    assert r.id == query.id
    assert r.response == hashing.encode("or", expected)


def test_oracle_lifecycle_debug():
    # registration
    EPOCH_CLI.set_native(False)
    oracle = _test_oracle_registration(ACCOUNT)
    # query
    query = _test_oracle_query(oracle, ACCOUNT_1, "{'city': 'Berlin'}")
    # respond
    _test_oracle_respond(oracle, query, ACCOUNT,  "{'temp_c': 20}")
    _test_oracle_response(query, "{'temp_c': 20}")


@pytest.mark.skip('Invalid query_id (TODO)')
def test_oracle_lifecycle_native():
    # registration
    EPOCH_CLI.set_native(True)
    oracle = _test_oracle_registration(ACCOUNT_1)
    # query
    query = _test_oracle_query(oracle, ACCOUNT, "{'city': 'Sofia'}")
    # respond
    _test_oracle_respond(oracle, query, ACCOUNT_1,  "{'temp_c': 2000}")
    _test_oracle_response(query, "{'temp_c': 2000}")
