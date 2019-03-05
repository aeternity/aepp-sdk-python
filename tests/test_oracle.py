import logging
import pytest

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


def _test_oracle_registration(node_cli, account):
    oracle = node_cli.Oracle()
    weather_oracle = dict(
        account=account,
        query_format="{'city': str}",
        response_format="{'temp_c': int}",
    )
    oracle.register(**weather_oracle)
    assert oracle.id == account.get_address().replace("ak_", "ok_")
    oracle_api_response = node_cli.get_oracle_by_pubkey(pubkey=oracle.id)
    assert oracle_api_response.id == oracle.id
    return oracle


def _test_oracle_query(node_cli, oracle, sender, query):
    q = node_cli.OracleQuery(oracle.id)
    q.execute(sender, query)
    return q


def _test_oracle_respond(oracle, query, account, response):
    oracle.respond(account, query.id, response)


def _test_oracle_response(query, expected):
    r = query.get_response_object()
    assert r.oracle_id == query.oracle_id
    assert r.id == query.id
    assert r.response == hashing.encode("or", expected)


@pytest.mark.skip('Debug transaction disabled')
def test_oracle_lifecycle_debug(chain_fixture):
    # registration
    # TODO: create a debug impl and test
    oracle = _test_oracle_registration(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)
    # query
    query = _test_oracle_query(chain_fixture.NODE_CLI, oracle, chain_fixture.ACCOUNT_1, "{'city': 'Berlin'}")
    # respond
    _test_oracle_respond(oracle, query, chain_fixture.ACCOUNT,  "{'temp_c': 20}")
    _test_oracle_response(query, "{'temp_c': 20}")


def test_oracle_lifecycle_native(chain_fixture):
    # registration
    oracle = _test_oracle_registration(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT_1)
    # query
    query = _test_oracle_query(chain_fixture.NODE_CLI, oracle, chain_fixture.ACCOUNT, "{'city': 'Sofia'}")
    # respond
    _test_oracle_respond(oracle, query, chain_fixture.ACCOUNT_1,  "{'temp_c': 2000}")
    _test_oracle_response(query, "{'temp_c': 2000}")
