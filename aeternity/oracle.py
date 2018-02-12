import logging

from aeternity.epoch import EpochComponent
from aeternity.utils import ValidateClassMixin

logger = logging.getLogger(__name__)




class OracleQuery(ValidateClassMixin):
    oracle_pubkey = None
    query_fee = None
    query_ttl = None
    response_ttl = None
    fee = None

    validate_attr_not_none = [
        'oracle_pubkey',
        'query_fee',
        'query_ttl',
        'response_ttl',
        'fee',
    ]

    def on_response(self, query):
        raise NotImplementedError('You must implement the `on_response` method')

    def query(self, query):
        cls = self.__class__
        message = {
            "target": "oracle",
            "action": "query",
            "payload": {
                "type": "OracleQueryTxObject",
                "vsn": 1,
                "oracle_pubkey": cls.oracle_pubkey,
                "query_fee": cls.query_fee,
                "query_ttl": {
                    "type": "delta", "value": cls.query_ttl
                },
                "response_ttl": {
                    "type": "delta", "value": cls.response_ttl
                },
                "fee": cls.fee,
                "query": query
            }
        }
        self.send(message)

    def on_mounted(self):
        cls = self.__class__
        message = {
            "target": "oracle",
            "action": "query",
            "payload": {
                "type": "OracleQueryTxObject",
                "vsn": 1,
                "oracle_pubkey": cls.oracle_pubkey,
                "query_fee": cls.query_fee,
                "query_ttl": {
                    "type": "delta", "value": cls.query_ttl
                },
                "response_ttl": {
                    "type": "delta", "value": cls.response_ttl
                },
                "fee": cls.fee,
                "query": query
            }
        }
        message = {
            "target": "oracle",
            "action": "subscribe",
            "payload": {"type": "response", "query_id": query_id}
        }
        return self.send_and_receive(message, print)


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
    default_query_ttl = None
    default_response_ttl = None

    message_listeners = [
        ('oracle', 'subscribed_to', 'handle_subscribed_to'),
    ]

    def __init__(self):
        super().__init__()
        # force the developer inheriting from this class to always specify these:
        self.assure_attr_not_none('query_format')
        self.assure_attr_not_none('response_format')
        self.assure_attr_not_none('default_query_fee')
        self.assure_attr_not_none('default_query_ttl')
        self.assure_attr_not_none('default_response_ttl')
        self.assure_attr_not_none('message_listeners')
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

    def get_response(self, message):
        raise NotImplementedError()


