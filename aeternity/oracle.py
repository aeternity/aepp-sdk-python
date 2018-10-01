import json
import logging


logger = logging.getLogger(__name__)


class NoOracleResponse(Exception):
    """raised when the Oracle refuses to respond to a query"""
    pass


class OracleQuery():
    message_listeners = [
        ('oracle', 'query', 'handle_oracle_query_sent'),
        ('chain', 'new_oracle_response', 'handle_oracle_response'),
        ('chain', 'subscription', 'handle_query_subscription_ack'),
    ]

    validate_attr_not_none = [
        'oracle_pubkey',
        'query_fee',
        'query_ttl',
        'response_ttl',
        'fee',
    ]

    def __init__(
        self,
        *,
        oracle_pubkey,
        query_fee,
        query_ttl,
        response_ttl,
        fee
    ):
        super().__init__()
        self.oracle_pubkey = oracle_pubkey
        self.query_fee = query_fee
        self.query_ttl = query_ttl
        self.response_ttl = response_ttl
        self.fee = fee

        self._last_query = None
        self.query_by_query_id = {}
        self.mounted = False
        self.client = None

    def on_response(self, response, query):
        raise NotImplementedError('You must implement the `on_response` method')

    def on_mounted(self, client):
        self.client = client
        self.mounted = True

    def query(self, query):
        if not self.mounted:
            raise RuntimeError('You must `mount` the OracleQuery before usage!')
        message = {
            "target": "oracle",
            "action": "query",
            "payload": {
                "type": "OracleQueryTxObject",
                "vsn": 1,
                "oracle_pubkey": self.oracle_pubkey,
                "query_fee": self.query_fee,
                "query_ttl": {
                    "type": "delta", "value": self.query_ttl
                },
                "response_ttl": {
                    "type": "delta", "value": self.response_ttl
                },
                "fee": self.fee,
                "query": query
            }
        }
        self.client.send(message)
        self._last_query = query

    def handle_oracle_query_sent(self, message):
        query_id = message['payload']['query_id']
        self._subscribe_to_query_id(query_id)

    def _subscribe_to_query_id(self, query_id):
        logger.debug('Query was sent. Subscribing to query with id %s', query_id)
        subscribe_message = {
            "target": "chain",
            "action": "subscribe",
            "payload": {"type": "oracle_response", 'query_id': query_id}
        }
        self.client.send(subscribe_message)

    def handle_query_subscription_ack(self, message):
        query_id = message['payload'].get('subscribed_to', {}).get('query_id')
        if query_id:
            logger.debug(f'Got subscription ack for query {query_id}')
            self.query_by_query_id[query_id] = self._last_query
            self._last_query = None

    def handle_oracle_response(self, message):
        query_id = message['payload']['query_id']
        try:
            query = self.query_by_query_id.pop(query_id)
        except KeyError:
            # this only happens if this instance did not send the initial
            # query. Should we forward this response to the `on_response`
            # handler anyways?
            query = None
        self.on_response(message, query)


class OracleState:
    NONE = 'NONE'
    REGISTRATION_REQUESTED = 'REGISTRATION_REQUESTED'
    SUBSCRIPTION_REQUESTED = 'SUBSCRIPTION_REQUESTED'
    READY = 'READY'


class Oracle():
    """
    This the base class to override when creating an Oracle

    e.g.

    class MyWeatherOracle(Oracle):
        def get_response(message):
            return 42

    """

    def get_response(self, message):
        raise NotImplementedError()

    message_listeners = [
        # ('oracle', 'subscribed_to', 'handle_subscribed_to'),
        ('chain', 'new_oracle_query', 'handle_oracle_query_received'),
        ('oracle', 'response', 'handle_response_sent'),
        ('oracle', 'register', 'handle_registration_response'),
        ('chain', 'subscribe', 'handle_oracle_subscription_ack'),
    ]

    def __init__(
        self,
        *,
        query_format,
        response_format,
        default_query_fee,
        default_fee,
        default_ttl,
        default_query_ttl,
        default_response_ttl,
    ):
        super().__init__()
        # force the developer inheriting from this class to always specify these:
        self.query_format = query_format
        self.response_format = response_format
        self.default_query_fee = default_query_fee
        self.default_fee = default_fee
        self.default_ttl = default_ttl
        self.default_query_ttl = default_query_ttl
        self.default_response_ttl = default_response_ttl

        self.oracle_id = None
        self.state = OracleState.NONE

    def is_ready(self):
        return self.state == OracleState.READY

    def on_mounted(self, client):
        if self.state == OracleState.NONE:
            raise ValueError('Cannot mount an oracle twice')

        pubkey = client.get_pubkey()
        # send oracle register signal to the node
        logger.debug('Sending OracleRegisterTx')
        register_message = {
            "target": "oracle",
            "action": "register",
            "payload": {
                "type": "OracleRegisterTxObject",
                "vsn": 1,
                "account": pubkey,
                "query_format": self.query_format,
                "response_format": self.response_format,
                "query_fee": self.get_query_fee(),
                "ttl": {
                    "type": "delta",
                    "value": self.default_ttl
                },
                "fee": self.get_fee()
            }
        }
        client.send(register_message)
        self.state = OracleState.REGISTRATION_REQUESTED
        self.client = client
        logger.debug('Waiting for OracleRegisterTx response')

    def handle_registration_response(self, message):
        if message['payload'].get('result') != 'ok':
            raise RuntimeError('Oracle registration failed!')
        self.oracle_id = message['payload']['oracle_id']
        logger.debug('Got OracleRegisterTx, oracle_id %s', self.oracle_id)
        logger.debug('Subscribing to oracles queries')
        subscribe_message = {
            "target": "chain",
            "action": "subscribe",
            "payload": {"type": "oracle_query", 'oracle_id': self.oracle_id}
        }
        self.client.send(subscribe_message)
        self.state = OracleState.SUBSCRIPTION_REQUESTED

    def handle_oracle_subscription_ack(self, message):
        oracle_id = message['payload'].get('subscribed_to', {}).get('oracle_id')
        if oracle_id:
            logger.debug(f'Subscribed to {oracle_id}')
            self.oracle_id = oracle_id
            self.state = OracleState.READY

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

    def handle_oracle_query_received(self, message):
        try:
            response = self.get_response(message)
        except NoOracleResponse:
            logger.debug('Oracle refused to respond')
        query_id = message['payload']['query_id']
        self.client.send({
            "target": "oracle",
            "action": "response",
            "payload": {
                "type": "OracleResponseTxObject",
                "vsn": 1,
                "query_id": query_id,
                "fee": self.get_fee(),
                "response": json.dumps(response),
            }
        })

    def handle_response_sent(self, message):
        logger.debug('Sending of response acknowledged by node. %s' % message)
