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


#
# Datatypes used for API responses:
#


AccountBalance = namedtuple('AccountBalance', [
    'pub_key', 'balance'
])
Transaction = namedtuple('Transaction', [
    'block_hash', 'block_height', 'hash', 'signatures', 'tx'
])
CoinbaseTx = namedtuple('CoinbaseTx', [
    'account', 'data_schema', 'type', 'vsn'
])
GenericTx = namedtuple('GenericTx', ['tx'])

Version = namedtuple('Version', [
    'genesis_hash', 'revision', 'version'
])

EpochInfo = namedtuple('EpochInfo', [
    'last_30_blocks_time'
])
LastBlockInfo = namedtuple('BlockInfo', [
    'difficulty', 'height', 'time', 'time_delta_to_parent'
])
BlockWithTx = namedtuple('BlockWithTx', [
    'data_schema', 'hash', 'height', 'nonce', 'pow', 'prev_hash', 'state_hash',
    'target', 'time', 'transactions', 'txs_hash', 'version'
])

def transaction_from_dict(data):
    if set(data.keys()) == {'tx'}:
        return GenericTx(**data)

    tx_type = data['tx']['type']
    if tx_type == 'coinbase':
        tx = CoinbaseTx(**data['tx'])
    else:
        raise ValueError(f'Cannot deserialize transaction of type {tx_type}')
    data = data.copy()  # don't mutate the input
    data['tx'] = tx
    return Transaction(**data)


def block_from_dict(data):
    data = data.copy()  # dont mutate the input
    data['transactions'] = [
        transaction_from_dict(tx) for tx in data.get('transactions', [])
    ]
    return BlockWithTx(**data)


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

    def http_json_call(self, method, base_url, endpoint, **kwargs):
        if endpoint.startswith('/'):  # strip leading slash to avoid petty errors
            endpoint = endpoint[1:]
        url = base_url + '/' + endpoint
        response = requests.request(method, url, **kwargs)
        if response.status_code >= 500:
            raise EpochRequestError(response)
        try:
            return response.json()
        except JSONDecodeError:
            raise EpochRequestError(response.text)

    def internal_http_get(self, endpoint, **kwargs):
        return self.http_json_call(
            'get', self._config.internal_api_url, endpoint, **kwargs
        )

    def internal_http_post(self, endpoint, **kwargs):
        return self.http_json_call(
            'post', self._config.internal_api_url, endpoint, **kwargs
        )

    def local_http_get(self, endpoint, **kwargs):
        return self.http_json_call(
            'get', self._config.http_api_url, endpoint, **kwargs
        )

    def local_http_post(self, endpoint, **kwargs):
        return self.http_json_call(
            'post', self._config.http_api_url, endpoint, **kwargs
        )

    def update_top_block(self):
        self._top_block = self.get_current_height()

    def wait_for_next_block(self):
        if self._top_block == None:
            self.update_top_block()
        while True:
            time.sleep(self.next_block_poll_interval_sec)
            new_block = self.get_current_height()
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

    #
    # API functions
    #

    def get_pubkey(self):
        return self._config.get_pubkey()

    def get_current_height(self):
        data = self.http_json_call('get', self._config.http_api_url, 'top')
        return int(data['height'])

    def get_balance(self, account_pubkey=None, height=None, hash=None):
        """
        get the balance of the account `account_pubkey`. If left empty, gets
        the balance of this node's account.

        To get a balance of the past use either the `height` or `hash` parameters

        :param account_pubkey:
        :param height:
        :param hash:
        :return:
        """
        assert not (height is not None and hash is not None), "Can only set either height or hash!"
        if account_pubkey is None:
            account_pubkey = self.get_pubkey()
        params = {}
        if height is not None:
            params['height'] = height
        if hash is not None:
            params['hash'] = hash
        return self.internal_http_get(f'account/balance/{account_pubkey}', params=params)['balance']

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
            tx_types=None,
            exclude_tx_types=None,
    ):
        """
        get the transactions of the account `account_pubkey`. If left empty, gets
        the transactions of this node's account.
        """
        if account_pubkey is None:
            account_pubkey = self.get_pubkey()

        params = {'tx_encoding': 'json'}
        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit
        params.update(self.make_tx_types_params(tx_types, exclude_tx_types))

        resp = self.internal_http_get(f'account/txs/{account_pubkey}', params=params)
        return [
            transaction_from_dict(transaction) for transaction in resp['transactions']
        ]

    def get_all_balances(self):
        # TODO: how does this call make any sense?? all balanaces?! --devsnd
        balance_dict_list = self.local_http_get('balances')['accounts_balances']
        return [AccountBalance(**balance) for balance in balance_dict_list]

    def get_version(self):
        return Version(**self.local_http_get('version'))

    def get_info(self):
        data = self.local_http_get('info')
        data['last_30_blocks_time'] = [
            # set `time_delta_to_parent` per default to None
            LastBlockInfo(**{'time_delta_to_parent': None, **blk})
            for blk in data['last_30_blocks_time']
        ]
        return EpochInfo(**data)

    def get_peers(self):
        # this is a debugging function
        # TODO
        raise NotImplementedError()

    def get_block_by_height(self, height):
        empty_block = {  # this data does not exist in the genesis block struct
            'pow': None, 'prev_hash': None, 'transactions': [],
            'txs_hash': None, 'data_schema': None, 'hash': None
        }
        data = self.local_http_get('block-by-height', params=dict(height=height))
        print(empty_block)
        print(data)
        return block_from_dict({**empty_block, **data})

    def get_block_by_hash(self, hash):
        data = self.local_http_get('block-by-hash', params=dict(hash=hash))
        # add this to make it compatible to the struct from `get_latest_block`
        data.update({'data_schema': None, 'hash': None})
        return block_from_dict(data)

    def get_genesis_block(self):
        data = self.internal_http_get('block/genesis', params=dict(tx_encoding='json'))
        # fill up the fields that cannot exist in the genesis block to make it
        # compatible with the `BlockWithTxs`
        data.update({'pow': None, 'prev_hash': None, 'transactions': [], 'txs_hash': None})
        return block_from_dict(data)

    def get_latest_block(self):
        data = self.internal_http_get('block/latest', params=dict(tx_encoding='json'))
        return block_from_dict(data)

    def get_pending_block(self):
        data = self.internal_http_get('block/pending', params=dict(tx_encoding='json'))
        missing_data = {'hash': None}  # the pending block cannot have a hash yet
        return block_from_dict({**missing_data, **data})

    def get_block_transaction_count_by_hash(
        self, _hash, tx_types=None, exclude_tx_types=None
    ):
        params = self.make_tx_types_params(tx_types, exclude_tx_types)
        data = self.internal_http_get(f'/block/txs/count/hash/{_hash}', params=params)
        return data['count']

    def get_block_transaction_count_by_height(
        self, height, tx_types=None, exclude_tx_types=None
    ):
        params = self.make_tx_types_params(tx_types, exclude_tx_types)
        data = self.internal_http_get(f'/block/txs/count/height/{height}', params=params)
        return data['count']

    def get_transaction_from_block_height(self, height, tx_idx):
        data = self.internal_http_get(
            f'block/tx/height/{height}/{tx_idx}',
            params={'tx_encoding': 'json'}
        )
        if data.get('reason'):
            raise EpochRequestError(data['reason'])
        return data

    def get_transaction_from_block_hash(self, block_hash, tx_idx):
        data = self.internal_http_get(
            f'block/tx/hash/{block_hash}/{tx_idx}',
            params={'tx_encoding': 'json'}
        )
        if data.get('reason'):
            raise EpochRequestError(data['reason'])
        return data

    def get_transaction_from_latest_block(self, tx_idx):
        return self.get_transaction_from_block_hash('latest', tx_idx)

    def get_transactions_in_block_range(self, from_height, to_height, tx_types=None, exclude_tx_types=None):
        '''Get transactions list from a block range by height'''
        params = {
            'from': from_height,
            'to': to_height,
            'tx_encoding': 'json'
        }
        params.update(self.make_tx_types_params(tx_types, exclude_tx_types))
        data = self.internal_http_get('/block/txs/list/height', params=params)
        return [transaction_from_dict(tx) for tx in data['transactions']]


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
