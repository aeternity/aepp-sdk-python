#!/usr/bin/env python
import json
import logging
import re

import requests

from aeternity import Config
from aeternity import EpochClient
from aeternity import Oracle


logging.basicConfig(level=logging.DEBUG)


class OraclefJean(Oracle):
    """
    An oracle that can provide data from JSON APIs from the web.

    Just provide an URL that returns JSON for a GET request

    And provide the a jq-style query:
        (but it's reduced to alphanumeric non-quoted key traversal for plain
        objects and lists, e.g.)

        {'this': {'is': ['some', 'awesome'], 'api': 'result'}}}

        with the parameter
            jq='.this.is[1]'
        would return
            "awesome"

    """

    def _error(self, message, data=None):
        if data is None:
            data = {}
        return {'status': 'error', 'message': message, 'data': data}

    def _success(self, data):
        return {'status': 'ok', 'message': '', 'data': data}

    def _jq_traverse(self, jq, data):
        assert jq.startswith('.')  # remove identity
        if jq == '.':
            return data
        ret_data = data
        for subpath in jq[1:].split('.'):
            obj_traverse = subpath
            list_index = None
            list_indexed_match = re.match('(\w*)\[(\d+:?\d*)\]', subpath)
            if list_indexed_match:
                obj_traverse, list_index = list_indexed_match.groups()
            if obj_traverse:
                ret_data = ret_data[obj_traverse]
            if list_index is not None:
                # slices
                if ':' in list_index:
                    start, end = list_index.split(':')
                    start, end = int(start), int(end)
                    ret_data = ret_data[start:end]
                else:
                    # indices
                    ret_data = ret_data[int(list_index)]
        return ret_data

    def get_response(self, message):
        payload_query = message['payload']['query']
        payload_query = json.loads(payload_query)
        try:
            url, jq = payload_query['url'], payload_query['jq']
        except (KeyError, AssertionError) as exc:
            print(exc)
            return self._error('malformed query')
        try:
            json_data = requests.get(url).json()
        except Exception:
            return self._error('request/json error')
        try:
            ret_data = self._jq_traverse(jq, json_data)
        except (KeyError, AssertionError):
            return self._error('error traversing json/invalid jq')
        # make sure the result is not huge
        ret_data = json.dumps(ret_data)
        if len(ret_data) > 1024:
            return self._error('return data is too big (>1024 bytes)')
        return self._success(ret_data)


dev1_config = Config(external_host=3013, internal_host=3113, websocket_host=3114)
oraclef_jean = OraclefJean(
    # example spec (this spec is fictional and will be defined later)
    query_format='''{'url': 'str', 'jq': 'str'}''',
    # example spec (this spec is fictional and will be defined later)
    response_format='''{'status': 'error'|'ok', 'message': 'str', 'data': {}}''',
    default_ttl=50,
    default_query_fee=4,
    default_fee=6,
    default_query_ttl=10,
    default_response_ttl=10,
)
client = EpochClient(configs=dev1_config)
client.register_oracle(oraclef_jean)
client.listen_until(oraclef_jean.is_ready)

print(f'''You can now query this oracle using the following parameters:
    oracle_pubkey: {oraclef_jean.oracle_id}
    query_fee: {oraclef_jean.get_query_fee()}
    query_ttl: {oraclef_jean.get_query_ttl()}
    response_ttl: {oraclef_jean.get_response_ttl()}
    fee: {oraclef_jean.get_fee()}
    query_format: {oraclef_jean.query_format}
''')
print('Oracle ready')
client.listen()
print('Oracle Stopped')
