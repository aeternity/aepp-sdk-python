import json
from collections import defaultdict
import logging

import time
import websocket

from aeternity.config import Config
from aeternity.exceptions import NameNotAvailable, InsufficientFundsException, TransactionNotFoundException, TransactionHashMismatch
from aeternity.signing import KeyPair
from aeternity.openapi import OpenAPICli
from aeternity.config import DEFAULT_TX_TTL, DEFAULT_FEE


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
            self.websocket = websocket.create_connection(self.config.websocket_url, timeout=1)

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
    next_block_poll_interval_sec = 3

    exception_by_reason = {
        'Name not found': NameNotAvailable,
        'No funds in account': InsufficientFundsException,
        'Transaction not found': TransactionNotFoundException,
    }

    def __init__(self, *, configs=None, retry=True):
        if configs is None:
            configs = Config.get_defaults()
        if isinstance(configs, Config):
            configs = [configs]
        self._configs = configs
        self._active_config_idx = 0
        self._listeners = defaultdict(list)
        self._connection = self._make_connection()
        self._top_block = None
        self._retry = retry

        # instantiate the request client
        self.cli = OpenAPICli(configs[0].api_url, configs[0].api_url_internal)

    # enable composition
    def __getattr__(self, attr):
        return getattr(self.cli, attr)

    def _get_active_config(self):
        return self._configs[self._active_config_idx]

    def _make_connection(self):
        return Connection(config=self._get_active_config())

    def _use_next_config(self):
        self._active_config_idx = (self._active_config_idx) + 1 % len(self._configs)
        logger.info(f'Trying next connection to: {self._get_active_config()}')
        self._connection = Connection(config=self._get_active_config())

    def update_top_block(self):
        self._top_block = self.get_top_block()

    def wait_n_blocks(self, block_count, polling_interval=1):
        self.update_top_block()
        current_block = self.get_top_block()
        target_block = current_block.height + block_count
        if polling_interval is None:
            polling_interval = self.next_block_poll_interval_sec
        while True:
            time.sleep(polling_interval)
            self.update_top_block()
            if self._top_block.height >= target_block:
                break

    def wait_for_next_block(self, polling_interval=1):
        """
        blocking method to wait for the next block to be mined
        shortcut for self.wait_n_blocks(1, polling_interval=polling_interval)
        """
        self.wait_n_blocks(1, polling_interval=polling_interval)

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

    def spend(self, keypair, recipient_pubkey, amount, tx_ttl=DEFAULT_TX_TTL):
        """create and execute a spend transaction"""
        transaction = self.create_spend_transaction(keypair.get_address(), recipient_pubkey, amount, tx_ttl=tx_ttl)
        tx = self.post_transaction(keypair, transaction)
        return tx

    def post_transaction(self, keypair, transaction):
        """
        post a transaction to the chain
        :return: the signed_transaction
        """
        signed_transaction, b58signature = keypair.sign_transaction(transaction)
        tx_hash = KeyPair.compute_tx_hash(signed_transaction)
        signed_transaction_reply = self.send_signed_transaction(signed_transaction)
        if signed_transaction_reply.tx_hash != tx_hash:
            raise TransactionHashMismatch(f"Transaction hash doesn't match, expected {tx_hash} got {signed_transaction_reply.tx_hash}")
        return signed_transaction_reply

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

    def listen_until(self, func, timeout=None):
        start = time.time()
        while True:
            if func():
                return
            if timeout is not None and time.time() > start + timeout:
                raise TimeoutError('Condition %s was never fulfilled' % func)

            try:
                self._tick()
            except websocket.WebSocketTimeoutException:
                pass  # the timeout is set to 1s on the connection
            except websocket.WebSocketConnectionClosedException:
                if not self._retry:
                    raise
                self._connection.close()
                self._use_next_config()
                logger.error('Connection closed by node, retrying in 5s...')
                time.sleep(5)
            except KeyboardInterrupt:
                self._connection.close()

    def listen(self):
        self.listen_until(lambda: False)

    def compute_absolute_ttl(self, ttl):
        """compute the absolute ttl by adding the ttl to the current height of the chain"""
        assert ttl > 0
        top = self.get_current_key_block_height()
        return top.height + ttl

    #
    # API functions
    #

    @classmethod
    def _get_burn_key(cls):
        keypair = KeyPair.generate()
        keypair.signing_key

    def create_spend_transaction(self, sender_id, recipient_id, amount, payload="", tx_ttl=DEFAULT_TX_TTL, fee=DEFAULT_FEE, nonce=0):
        """
        create a spend transaction
        :param sender: the public key of the sender
        :param recipient: the public key of the recipient
        :param amount: the amount to send
        :param fee: the fee for the transaction
        """
        # compute the absolute ttl
        ttl = self.compute_absolute_ttl(tx_ttl)
        # send the update transaction
        body = {
            "recipient_id": recipient_id,
            "amount": amount,
            "fee":  fee,
            "sender_id": sender_id,
            "payload": payload,
            "ttl": ttl,
        }
        if nonce > 0:
            body['nonce'] = nonce
        return self.cli.post_spend(body=body)

    def send_signed_transaction(self, encoded_signed_transaction):
        """
        Utility method to post a transaction to the chain
        """
        return self.cli.post_transaction(body={"tx": encoded_signed_transaction})


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
