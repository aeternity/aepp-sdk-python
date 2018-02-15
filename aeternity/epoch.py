import json
from collections import defaultdict, namedtuple
import logging

from json import JSONDecodeError

import requests
import time
import websocket

from aeternity.config import Config
from aeternity.utils import ValidateClassMixin

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
            self.websocket = websocket.create_connection(self.config.websocket_url)

    def receive(self):
        self.assure_connected()
        message = json.loads(self.websocket.recv())
        logger.debug('RECEIVED: %s', message)
        return message

    def send(self, message):
        self.assure_connected()
        logger.debug('SENDING: %s', message)
        self.websocket.send(json.dumps(message))


class EpochRequestError(Exception):
    pass


class EpochClient:
    next_block_poll_interval_sec = 10

    def __init__(self, *, config=None, retry=True):
        if config is None:
            config = Config.get_default()
        self._config = config
        self._listeners = defaultdict(list)
        self._connection = Connection(config=config)
        self._top_block = None
        self._retry = retry
        self.send(
            {"target":"chain", "action":"subscribe", "payload":{"type":"new_block"}}
        )

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
        data = self.http_call('get', self._config.http_api_url, 'top')
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

    def dispatch_message(self, message):
        subscription_id = (message['origin'], message['action'])
        callbacks = self._listeners[subscription_id]
        logging.debug('DISPATCH: message %s to callbacks %s', subscription_id, callbacks)
        for callback in callbacks:
            callback(message)

    def mount(self, component):
        for target, action, callback_name in component.message_listeners:
            callback = getattr(component, callback_name)
            self._listeners[(target, action)].append(callback)
        component.on_mounted(self)

    register_oracle = mount

    def unmount(self, component):
        for target, action, callback in component.get_message_listeners():
            self._listeners[(target, action)].remove(callback)

    def send(self, message):
        self.update_top_block()
        self._connection.send(message)

    def spend(self, recipient_pubkey, amount):
        data = {"recipient_pubkey": recipient_pubkey,
                "amount": int(amount),
                "fee": 1}
        logging.debug('Spend: sending data %s to %s', json.dumps(data),
                      self._config.spend_url)
        requests.post(self._config.spend_url, json=data)

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

    def _tick(self):
        message = self._connection.receive()
        self.dispatch_message(message)

    def consume_until(self, func, timeout=None):
        start = time.time()
        while True:
            if timeout is not None and time.time() > start + timeout:
                raise TimeoutError('Condition %s was never fulfilled' % func)
            self._tick()
            if func():
                return

    def run(self):
        try:
            while True:
                try:
                    self._tick()
                except websocket.WebSocketConnectionClosedException:
                    if not self._retry:
                        raise
                    self._connection.close()
                    logger.error('Connection closed by node, retrying in 5s...')
                    time.sleep(5)
        except KeyboardInterrupt:
            self._connection.close()
            return


class EpochSubscription():
    message_listeners = None

    # Message listeners are a list of tuples to define how the class should
    # react to incoming messages, for example:
    #
    # message_listeners = [
    #     ('target', 'action', 'handler_method_name'),
    #     # e.g.
    #     ('oracle', 'subscribed_to', 'handle_subscribed_to'),
    # ]

    def __init__(self):
        super().__init__()
        assert self.message_listeners is not None, \
            'Classes inheriting EpochSubscription must have message_listeners'

    def on_mounted(self, client):
        """
        on_mounted is called just after the EpochClient has registered all the
        message_listeners. This can be used to send initial messages to the node

        :param client: the EpochClient instance
        :return: None
        """
        pass
