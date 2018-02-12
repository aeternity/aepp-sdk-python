import json
from collections import defaultdict, namedtuple

import logging
from json import JSONDecodeError

import requests
import time
import websocket

from aeternity.config import Config

logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, config):
        self.config = config
        self.websocket = None

    def close(self):
        self.websocket.close()
        self.websocket = None

    def assure_connected(self):
        if self.websocket is None:
            self.websocket = websocket.create_connection(self.config.websocker_url)

    def receive(self):
        self.assure_connected()
        message = json.loads(self.websocket.recv())
        logger.debug('received: %s', message)
        return message

    def send(self, message):
        self.assure_connected()
        logger.debug('sending: %s', message)
        self.websocket.send(json.dumps(message))


class EpochRequestError(Exception):
    pass


class EpochClient:
    next_block_poll_interval_sec = 10

    def __init__(self, config=None):
        if config is None:
            config = Config.get_default()
        self._config = config
        self._listeners = defaultdict(list)
        self._connection = Connection(config=config)
        self._top_block = None
        # self.send_and_receive(
        #     {"target":"chain", "action":"subscribe", "payload":{"type":"mined_block"}},
        #     print
        # )

    def http_call(self, method, base_url, endpoint, **kwargs):
        url = base_url + '/' + endpoint
        response = requests.request(method, url, **kwargs)
        if response.status_code >= 500:
            raise EpochRequestError(response)
        try:
            return response.json()
        except JSONDecodeError:
            raise EpochRequestError(response.text)

    def internal_http_get(self, endpoint, **kwargs):
        return self.http_call(
            'get', self._config.internal_api_url, endpoint, **kwargs
        )

    def internal_http_post(self, endpoint, **kwargs):
        return self.http_call(
            'post', self._config.internal_api_url, endpoint, **kwargs
        )

    def local_http_get(self, endpoint, **kwargs):
        return self.http_call(
            'get', self._config.http_api_url, endpoint, **kwargs
        )

    def local_http_post(self, endpoint, **kwargs):
        return self.http_call(
            'post', self._config.http_api_url, endpoint, **kwargs
        )

    def get_pubkey(self):
        return self._config.get_pubkey()

    def get_top_block(self):
        data = requests.get(self._config.top_block_url).json()
        return int(data['height'])

    def update_top_block(self):
        self._top_block = self.get_top_block()

    def wait_for_next_block(self):
        if self._top_block == None:
            self.update_top_block()
        while True:
            time.sleep(self.next_block_poll_interval_sec)
            new_block = self.get_top_block()
            if (new_block > self._top_block):
                self._top_block = new_block
                break

    def add_listener(self, target, action, callback):
        self._listeners[(target, action)].append(callback)

    def remove_listener(self, target, action, callback):
        self._listeners[(target, action)].remove(callback)

    def dispatch_message(self, message):
        for callback in self._listeners[(message['origin'], message['action'])]:
            callback(message)

    def mount(self, component):
        for target, action, callback_name in component.message_listeners:
            callback = getattr(component, callback_name)
            self.add_listener(target, action, callback)
            component.on_mounted(self)

    register_oracle = mount

    def unmount(self, component):
        for target, action, callback in component.get_message_listeners():
            self.add_listener(target, action, callback)

    def send(self, message):
        self.update_top_block()
        self._connection.send(message)

    def send_and_receive(self, message):
        """
        This is a workaround for the problem described here:
        https://github.com/aeternity/epoch/issues/708

        This is a blocking operation that will send a message and wait for a
        response from the node. This is needed because there is yet no mechanism
        for marking messages with a unique id that is returned in the response,
        so we cannot know which response belongs to which request. The best we
        can do for now is just not sending multiple requests concurrently and
        assume that the first response is the response to this request.

        :param message:
        :param receive_callback:
        :return:
        """
        self.send(message)
        return self._connection.receive()

    def run(self):
        try:
            while True:
                try:
                    message = self._connection.receive()
                    self.dispatch_message(message)
                except websocket.WebSocketConnectionClosedException:
                    self._connection.close()
                    logger.error('Connection closed by node, retrying in 5s...')
                    time.sleep(5)
        except KeyboardInterrupt:
            self._connection.close()
            return

    def ask_oracle(
        self,
        oracle_pubkey,
        query_fee,
        query_ttl,
        response_ttl,
        fee,
        query
    ):
        message = {
            "target": "oracle",
            "action": "query",
            "payload": {
                "type": "OracleQueryTxObject",
                "vsn": 1,
                "oracle_pubkey": oracle_pubkey,
                "query_fee": int(query_fee),
                "query_ttl": {
                    "type": "delta", "value": int(query_ttl)
                },
                "response_ttl": {
                    "type": "delta", "value": int(response_ttl)
                },
                "fee": int(fee),
                "query": query
            }
        }
        self.send(message)

    def subscribe_oracle(self, query_id):
        message = {
            "target": "oracle",
            "action": "subscribe",
            "payload": {"type": "response", "query_id": query_id}
        }
        return self.send_and_receive(message, print)


class EpochComponent:
    message_listeners = None

    # Message listeners are a list of tuples to define how the class should
    # react to incoming messages, for example:
    #
    # message_listeners = [
    #     ('target', 'action', 'handler_method_name'),
    #     # e.g.
    #     ('oracle', 'subscribed_to', 'handle_subscribed_to'),
    # ]

    def _assure_attr_not_none(self, attrname):
        if not hasattr(self.__class__, attrname) or getattr(self.__class__, attrname, None) is None:
            raise ValueError(f'You must specify `{attrname}` on {self.__class__}')

    def __init__(self):
        self._assure_attr_not_none('message_listeners')

    def on_mounted(self, client):
        """
        on_mounted is called just after the EpochClient has registered all the
        message_listeners. This can be used to send initial messages to the node

        :param client: the EpochClient instance
        :return: None
        """
        pass


class OracleRegistrationFailed(Exception):
    pass


class Oracle(EpochComponent):
    """
    This a the base class to override when creating an Oracle

    e.g.

    class MyWeatherOracle(Oracle):
        query_format = 'weather_query'
        response_format = 'weather_resp'
        default_query_fee = 0
        default_fee = 6
        default_ttl = 2000

    """
    query_format = None
    response_format = None
    default_query_fee = None
    default_fee = None
    default_query_ttl = None
    default_response_ttl = None

    message_listeners = [
        ('oracle', 'subscribed_to', 'handle_subscribed_to'),
    ]

    def __init__(self):
        super().__init__()
        # force the developer inheriting from this class to always specify these:
        self._assure_attr_not_none('query_format')
        self._assure_attr_not_none('response_format')
        self._assure_attr_not_none('default_query_fee')
        self._assure_attr_not_none('default_query_ttl')
        self._assure_attr_not_none('default_response_ttl')
        self._assure_attr_not_none('message_listeners')
        self.oracle_id = None
        self.subscribed_to_queries = False

    def on_mounted(self, client):
        pubkey = client.get_pubkey()
        # send oracle register signal to the node
        register_message = {
            "target": "oracle",
            "action": "register",
            "payload": {
                "type": "OracleRegisterTxObject",
                "vsn": 1,
                "account": pubkey,
                "query_format": self.__class__.query_format,
                "response_format": self.__class__.response_format,
                "query_fee": self.get_query_fee(),
                "ttl": {
                    "type": "delta",
                    "value": self.get_query_ttl()
                },
                "fee": self.get_fee()
            }
        }
        register_response = client.send_and_receive(register_message)
        if register_response['payload'].get('result') != 'ok':
            raise OracleRegistrationFailed(register_response)
        self.oracle_id = register_response['payload']['oracle_id']

        subscribe_message = {
            "target": "chain",
            "action": "subscribe",
            "payload": {"type": "query", 'oracle_id': self.oracle_id}
        }
        subscribe_response = client.send_and_receive(subscribe_message)
        if subscribe_response['payload'].get('result') != 'ok':
            raise OracleRegistrationFailed(subscribe_response)
        subscribed_to = subscribe_response['payload']['subscribed_to']
        logger.debug(f'Subscribed to {subscribed_to}')
        self.subscribed_to_queries = True

    def get_query_fee(self):
        # TODO: does is make sense to make this variable during runtime?
        return self.default_query_fee

    def get_fee(self):
        return self.default_fee

    def get_query_ttl(self):
        # TODO: does is make sense to make this variable during runtime?
        return self.default_query_ttl

    def get_response_ttl(self):
        return self.default_response_ttl

    def handle_subscribed_to(self, message):
        print('handle_subscribed_to')
        print(message)
        # message['payload']['subscribed_to']['oracle_id']

    def get_reply(self, message):
        raise NotImplementedError()

    def _respond_to_query(self, query_id, request):
        self.send({
            "target": "oracle",
            "action": "response",
            "payload": {
                "type": "OracleResponseTxObject",
                "vsn": 1,
                "query_id": query_id,
                "fee": self.get_query_fee(),
                "response": self.get_reply(request)
            }
        })
