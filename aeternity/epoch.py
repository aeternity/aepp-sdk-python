import json
from collections import defaultdict, namedtuple
import logging

import time
import websocket

from aeternity.exceptions import NameNotAvailable, InsufficientFundsException, TransactionNotFoundException
from aeternity import config, aens, openapi, transactions, contract


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

    exception_by_reason = {
        'Name not found': NameNotAvailable,
        'No funds in account': InsufficientFundsException,
        'Transaction not found': TransactionNotFoundException,
    }

    def __init__(self, configs=None, blocking_mode=False, retry=True, debug=False):
        if configs is None:
            configs = config.Config.get_defaults()
        if isinstance(configs, config.Config):
            configs = [configs]
        self._configs = configs
        self._active_config_idx = 0
        self._listeners = defaultdict(list)
        self._connection = self._make_connection()
        self._top_block = None
        self._retry = retry
        # instantiate the request client
        self.cli = openapi.OpenAPICli(configs[0].api_url, configs[0].api_url_internal, debug=debug)
        # shall the client work in blocking mode
        self.blocking_mode = blocking_mode

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

    def get_top_block(self):
        """
        Override the native method to transform the get top block response object
        to a Block
        """
        b = self.cli.get_top_block()
        if hasattr(b, 'key_block'):
            return namedtuple('Block', sorted(b.key_block))(**b.key_block)
        else:
            return namedtuple('Block', sorted(b.micro_block))(**b.micro_block)

    def get_block_by_hash(self, hash=None):
        """
        Retrieve a key block or a micro block header
        based on the block hash_prefix
        :param block_hash: either a key block or micro block hash
        """
        block = None
        if hash is None:
            return block

        if hash.startswith("kh_"):
            # key block
            block = self.cli.get_key_block_by_hash(hash=hash)
        elif hash.startswith("mh_"):
            # micro block
            block = self.cli.get_micro_block_header_by_hash(hash=hash)
        return block

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

    def spend(self, keypair, recipient_pubkey, amount, payload="", fee=config.DEFAULT_FEE, tx_ttl=config.DEFAULT_TX_TTL):
        """create and execute a spend transaction"""
        txb = transactions.TxBuilder(self.cli, keypair)
        # create spend_tx
        tx, sg, tx_hash = txb.tx_spend(recipient_pubkey, amount, payload, fee, tx_ttl)
        # post the transaction to the chain
        txb.post_transaction(tx, tx_hash)
        if self.blocking_mode:
            txb.wait_tx(tx_hash)
        return tx, sg, tx_hash

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

    # support naming
    def AEName(self, domain):
        return aens.AEName(domain, client=self)

    # support contract
    def Contract(self, source_code, bytecode=None, address=None, abi=contract.Contract.SOPHIA):
        return contract.Contract(source_code, client=self, bytecode=bytecode, address=address, abi=abi)


class EpochSubscription:
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
        if self.message_listeners is not None:
            raise ValueError('Classes inheriting EpochSubscription must have message_listeners')

    def on_mounted(self, client):
        """
        on_mounted is called just after the EpochClient has registered all the
        message_listeners. This can be used to send initial messages to the node

        :param client: the EpochClient instance
        :return: None
        """
        pass
