import logging

from aeternity.epoch import EpochComponent

logger = logging.getLogger(__name__)


class OracleQuerySubscriptionFailed(Exception):
    pass


class OracleQuery(EpochComponent):
    oracle_pubkey = None
    query_fee = None
    query_ttl = None
    response_ttl = None
    fee = None

    message_listeners = [
        ('oracle', 'query', 'handle_oracle_query_sent'),
        ('chain', 'new_oracle_response', 'handle_oracle_response'),
    ]

    validate_attr_not_none = [
        'oracle_pubkey',
        'query_fee',
        'query_ttl',
        'response_ttl',
        'fee',
    ]

    def __init__(self, oracle_pubkey=None):
        self.mounted = False
        self.client = None
        if oracle_pubkey is not None:
            self.oracle_pubkey = oracle_pubkey
        super().__init__()
        self.query_ids = []

    def on_response(self, response, query):
        raise NotImplementedError('You must implement the `on_response` method')

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

    def handle_oracle_query_sent(self, message):
        query_id = message['payload']['query_id']
        logger.debug('Query was sent. Subscribing to query with id %s', query_id)
        subscribe_message = {
            "target": "chain",
            "action": "subscribe",
            "payload": {"type": "oracle_response", 'query_id': query_id}
        }
        self.client.send(subscribe_message)

    def handle_oracle_response(self, message):
        self.on_response(message, 'TODO: get the initial query in here.')

    def on_mounted(self, client):
        self.client = client
        self.mounted = True


class OracleRegistrationFailed(Exception):
    pass


class Oracle(EpochComponent):
    """
    This the base class to override when creating an Oracle

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
    default_ttl = None
    default_query_ttl = None
    default_response_ttl = None

    def get_response(self, message):
        raise NotImplementedError()

    message_listeners = [
        # ('oracle', 'subscribed_to', 'handle_subscribed_to'),
        ('chain', 'new_oracle_query', 'handle_oracle_query_received'),
        ('oracle', 'response', 'handle_response_sent'),
        ('oracle', 'register', 'handle_registration_response'),
        ('chain', 'register', 'handle_oracle_registration'),
    ]

    def __init__(self):
        super().__init__()
        # force the developer inheriting from this class to always specify these:
        self.assure_attr_not_none('query_format')
        self.assure_attr_not_none('response_format')
        self.assure_attr_not_none('default_query_fee')
        self.assure_attr_not_none('default_ttl')
        self.assure_attr_not_none('default_query_ttl')
        self.assure_attr_not_none('default_response_ttl')
        self.assure_attr_not_none('message_listeners')
        self.oracle_id = None
        self.oracle_registered = False
        self.subscribed_to_queries = False
        self.mounted = False

    def on_mounted(self, client):
        assert not self.mounted, 'Cannot mount an oracle twice'
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
                "query_format": self.__class__.query_format,
                "response_format": self.__class__.response_format,
                "query_fee": self.get_query_fee(),
                "ttl": {
                    "type": "delta",
                    "value": self.default_ttl
                },
                "fee": self.get_fee()
            }
        }
        logger.debug('Waiting for OracleRegisterTx response')
        client.send(register_message)
        self.client = client
        self.mounted = True

    def handle_registration_response(self, message):
        if message['payload'].get('result') != 'ok':
            raise OracleRegistrationFailed(message)
        self.oracle_id = message['payload']['oracle_id']
        logger.debug('Got OracleRegisterTx, oracle_id %s', self.oracle_id)
        logger.debug('Subscribing to oracles queries')
        subscribe_message = {
            "target": "chain",
            "action": "subscribe",
            "payload": {"type": "oracle_query", 'oracle_id': self.oracle_id}
        }
        self.client.send(subscribe_message)
        self.oracle_registered = True

    def handle_oracle_registration(self, message):
        message = {
            'action': 'register',
            'origin': 'oracle',
            'payload': {
                'result': 'ok',
                'oracle_id': 'ok$3WRqCYwdr9B5aeAMT7Bfv2gGZpLUdD4RQM4hzFRpRzRRZx7d8pohQ6xviXxDTLHVwWKDbGzxH1xRp19LtwBypFpCVBDjEQ',
                'tx_hash': 'th$bRFKbTNEMhUJE23G6d7XLkrKcivaDuH6nihkKmqQPzxp4nocz'
            }
        }
        oracle_id = message['payload'].get('oracle_id')
        if oracle_id:
            logger.debug(f'Subscribed to {subscribed_to}')
            self.oracle_id = oracle_id
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

    def handle_oracle_query_received(self, message):
        response = self.get_response(message)
        query_id = message['payload']['query_id']
        self.client.send({
            "target": "oracle",
            "action": "response",
            "payload": {
                "type": "OracleResponseTxObject",
                "vsn": 1,
                "query_id": query_id,
                "fee": self.get_fee(),
                "response": response
            }
        })

    def handle_response_sent(self, message):
        logger.debug('Sending of response acknowledged by node. %s' % message)


