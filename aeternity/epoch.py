import json
from collections import defaultdict
import logging
import os

import time
import websocket

from aeternity.config import Config
from aeternity.exceptions import NameNotAvailable, InsufficientFundsException, TransactionNotFoundException
from aeternity.signing import KeyPair
from aeternity.openapi import OpenAPICli

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


# #
# # Datatypes used for API responses:
# #

# AccountBalance = namedtuple('AccountBalance', [
#     'pub_key', 'balance'
# ])

# # Wrapper Datatype for all transactions
# Transaction = namedtuple('Transaction', [
#     'block_hash', 'block_height', 'hash', 'signatures', 'tx', 'data_schema'
# ])
# #
# # Transaction types:
# #
# CoinbaseTx = namedtuple('CoinbaseTx', [
#     'block_height', 'account', 'data_schema', 'type', 'vsn', 'reward'
# ])
# AENSClaimTx = namedtuple('AENSClaimTx', [
#     'account', 'fee', 'name', 'name_salt', 'nonce', 'type', 'vsn'
# ])
# AENSPreclaimTx = namedtuple('AENSPreclaimTx', [
#     'account', 'commitment', 'fee', 'nonce', 'type', 'vsn'
# ])
# AENSTransferTx = namedtuple('AENSTransferTx', [
#     'account', 'fee', 'name_hash', 'nonce', 'recipient_pubkey', 'type', 'vsn'
# ])
# AENSUpdateTX = namedtuple('AENSUpdateTx', [
#     'account', 'fee', 'name_hash', 'name_ttl', 'nonce', 'pointers', 'ttl',
#     'type', 'vsn'
# ])
# SpendTx = namedtuple('SpendTx', [
#     'data_schema', 'type', 'vsn', 'amount', 'fee', 'nonce', 'recipient', 'sender'
# ])
# AEOQueryTx = namedtuple('AEOQueryTx', [
#     'data_schema', 'fee', 'nonce', 'oracle', 'query', 'query_fee', 'query_ttl',
#     'response_ttl', 'sender', 'type', 'vsn'
# ])
# AEOResponseTx = namedtuple('AEOResponseTx', [
#     'data_schema', 'fee', 'nonce', 'oracle', 'query_id', 'response', 'type', 'vsn'
# ])
# AEORegisterTx = namedtuple('AEORegisterTx', [
#     'account', 'data_schema', 'fee', 'nonce', 'query_fee', 'query_spec',
#     'response_spec', 'ttl', 'type', 'vsn'
# ])
# GenericTx = namedtuple('GenericTx', ['tx'])


# Version = namedtuple('Version', [
#     'genesis_hash', 'revision', 'version'
# ])
# EpochInfo = namedtuple('EpochInfo', [
#     'last_30_blocks_time'
# ])
# LastBlockInfo = namedtuple('BlockInfo', [
#     'difficulty', 'height', 'time', 'time_delta_to_parent'
# ])
# BlockWithTx = namedtuple('BlockWithTx', [
#     'data_schema', 'hash', 'height', 'nonce', 'pow', 'prev_hash', 'state_hash',
#     'target', 'time', 'transactions', 'txs_hash', 'version'
# ])

# # NewTransaction is the container when creating a transaction using the epoch
# # node, which then can be signed offline
# NewTransaction = namedtuple('NewTransaction', ['tx', 'tx_hash'])


# transaction_type_mapping = {
#     'coinbase_tx': CoinbaseTx,
#     'aec_coinbase_tx': CoinbaseTx,
#     'aec_spend_tx': SpendTx,
#     'spend_tx': SpendTx,
#     'aens_claim_tx': AENSClaimTx,
#     'aens_preclaim_tx': AENSPreclaimTx,
#     'aens_transfer_tx': AENSTransferTx,
#     'aens_update_tx': AENSUpdateTX,
#     'aeo_query_tx': AEOQueryTx,
#     'aeo_register_tx': AEORegisterTx,
#     'aeo_response_tx': AEOResponseTx,
# }


# def transaction_from_dict(data):
#     if set(data.keys()) == {'tx'}:
#         return GenericTx(**data)

#     tx_type = data['tx']['type']
#     try:
#         tx = transaction_type_mapping[tx_type](**data['tx'])
#     except KeyError:
#         raise ValueError(f'Cannot deserialize transaction of type {tx_type}')

#     data = data.copy()  # don't mutate the input
#     data['tx'] = tx
#     if 'data_schema' not in data:
#         data['data_schema'] = None
#         # TODO: The API should provide a data_schema for all objects
#         logger.debug('Deserialized transaction without data_schema!')
#     return Transaction(**data)


# def block_from_dict(data):
#     data = data.copy()  # dont mutate the input
#     data['transactions'] = [
#         transaction_from_dict(tx) for tx in data.get('transactions', [])
#     ]
#     return BlockWithTx(**data)


class EpochClient:
    next_block_poll_interval_sec = 0.01

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

        # find out the version of the node we are connecting to
        swagger_file = f'assets/swagger/{configs[0].node_version}.json'
        if not os.path.exists(swagger_file):
            raise Exception(f"node version {configs[0].node_version} not supported")
        # instantiate the request client
        self.cli = OpenAPICli(swagger_file, configs[0].http_api_url, configs[0].internal_api_url)

    def _get_active_config(self):
        return self._configs[self._active_config_idx]

    def _make_connection(self):
        return Connection(config=self._get_active_config())

    def _use_next_config(self):
        self._active_config_idx = (self._active_config_idx) + 1 % len(self._configs)
        logger.info(f'Trying next connection to: {self._get_active_config()}')
        self._connection = Connection(config=self._get_active_config())

    def update_top_block(self):
        self._top_block = self.get_height()

    def wait_n_blocks(self, block_count, polling_interval=None):
        self.update_top_block()
        current_block = self.get_height()
        target_block = current_block + block_count
        if polling_interval is None:
            polling_interval = self.next_block_poll_interval_sec
        while True:
            time.sleep(polling_interval)
            self.update_top_block()
            if self._top_block >= target_block:
                break

    def wait_for_next_block(self, polling_interval=None):
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

    def spend(self, keypair, recipient_pubkey, amount):
        transaction = self.create_spend_transaction(recipient_pubkey, amount, sender=keypair)
        signed_transaction, signature = keypair.sign_transaction(transaction)
        resp = self.send_signed_transaction(signed_transaction)
        return resp, transaction.tx_hash

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

    #
    # API functions
    #

    @classmethod
    def _get_burn_key(cls):
        keypair = KeyPair.generate()
        keypair.signing_key

    def get_pubkey(self):
        pub_key = self.internal_http_get('account/pub-key')
        return pub_key['pub_key']

    def get_height(self):
        top = self.cli.get_top()
        logging.debug(f"get_height: {top}")
        return top.height

    def get_balance(self, account_pubkey=None, height=None, block_hash=None):
        """
        get the balance of the account `account_pubkey`. If left empty, gets
        the balance of this node's account.

        To get a balance of the past use either the `height` or `hash` parameters

        :param account_pubkey:
        :param height:
        :param block_hash:
        :return:
        """
        assert not (height is not None and block_hash is not None), "Can only set either height or hash!"
        balance = self.cli.get_account_balance(
            account_pubkey=account_pubkey, height=height, block_hash=block_hash
        )
        return balance.balance

    @classmethod
    def make_tx_types_params(cls, tx_types=None, exclude_tx_types=None):
        params = {}
        if tx_types is not None:
            params['tx_types'] = ','.join(tx_types)
        if exclude_tx_types is not None:
            params['exclude_tx_types'] = ','.join(exclude_tx_types)
        return params

    def get_transactions(
            self,
            account_pubkey=None,
            offset=None,
            limit=None,
            tx_types=[],
            exclude_tx_types=[],
    ):
        """
        get the transactions of the account `account_pubkey`. If left empty, gets
        the transactions of this node's account.
        """
        return self.cli.get_account_transactions(account_pubkey=account_pubkey,
                                                 tx_encoding='json',
                                                 offset=offset,
                                                 limit=limit,
                                                 tx_types=','.join(tx_types),
                                                 exclude_tx_types=','.join(exclude_tx_types),)

    def get_version(self):
        # return Version(**self.external_http_get('version'))
        pass

    def get_info(self):
        # TODO: write test for this one
        pass

    def get_peers(self):
        # this is a debugging function
        # TODO: whi is this here?
        raise NotImplementedError()

    def get_block_by_height(self, height):
        return self.cli.get_block_by_height(height=height)

    def get_block_by_hash(self, hash):
        return self.cli.get_block_by_hash(hash=hash)

    def get_genesis_block(self):
        return self.cli.get_block_genesis()

    def get_latest_block(self):
        return self.cli.get_block_latest()

    def get_pending_block(self):
        return self.cli.get_block_pending()

    def get_block_transaction_count_by_hash(self, _hash, tx_types=None, exclude_tx_types=None):
        return self.cli.get_block_txs_count_by_hash(hash=_hash, tx_types=tx_types, exclude_tx_types=exclude_tx_types)

    def get_block_transaction_count_by_height(self, height, tx_types=None, exclude_tx_types=None):

        return self.cli.get_block_txs_count_by_height(height=height, tx_types=tx_types, exclude_tx_types=exclude_tx_types)

    def get_transaction_by_transaction_hash(self, tx_hash):
        assert tx_hash.startswith('th$'), 'A transaction hash must start with "th$"'
        return self.cli.get_tx(tx_hash=tx_hash)

    def get_transaction_from_block_height(self, height, tx_index):
        return self.cli.get_transaction_from_block_height(height=height, tx_index=tx_index)

    def get_transaction_from_block_hash(self, block_hash, tx_index):
        return self.cli.get_transaction_from_block_hash(hash=block_hash, tx_index=tx_index)

    def get_transaction_from_latest_block(self, tx_idx):
        return self.get_transaction_from_block_hash('latest', tx_idx)

    def get_transactions_in_block_range(self, from_height, to_height, tx_types=None, exclude_tx_types=None):
        '''Get transactions list from a block range by height'''
        return self.cli.get_txs_list_from_block_range_by_height(
            _from=from_height,
            to=to_height,
            tx_types=tx_types,
            exclude_tx_types=exclude_tx_types
        )

    def create_spend_transaction(self, sender_pubkey, recipient_pubkey, amount, fee=1, nonce=0, payload="payload"):
        """
        create a spend transaction
        :param sender: the public key of the sender
        :param recipient: the public key of the recipient
        :param amount: the amount to send
        :param fee: the fee for the transaction
        """
        body = {
            "recipient_pubkey": recipient_pubkey,
            "amount": amount,
            "fee":  fee,
            "sender": sender_pubkey,
            "payload": payload,
        }
        if nonce > 0:
            body['nonce'] = nonce
        return self.cli.post_spend(body=body)

    def send_signed_transaction(self, encoded_signed_transaction):
        return self.cli.post_tx(body={"tx": encoded_signed_transaction})


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
