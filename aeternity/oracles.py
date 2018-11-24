import logging
from aeternity import config, hashing

logger = logging.getLogger(__name__)


class OracleQuery():
    """
    Create and execute a oracle query
    """

    def __init__(self, client, oracle_id, id=None):
        self.oracle_id = oracle_id
        self.id = id
        self.client = client

    def execute(self, sender, query,
                query_fee=config.ORACLE_DEFAULT_QUERY_FEE,
                query_ttl_type=config.ORACLE_DEFAULT_TTL_TYPE_DELTA,
                query_ttl_value=config.ORACLE_DEFAULT_QUERY_TTL_VALUE,
                response_ttl_type=config.ORACLE_DEFAULT_TTL_TYPE_DELTA,
                response_ttl_value=config.ORACLE_DEFAULT_RESPONSE_TTL_VALUE,
                fee=config.DEFAULT_FEE,
                tx_ttl=config.DEFAULT_TX_TTL):
        """
        Execute a query to the oracle
        """
        if self.oracle_id is None:
            raise ValueError("Oracle id must be provided before executing a query")
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(sender.get_address(), tx_ttl)
        # create spend_tx
        tx = txb.tx_oracle_query(self.oracle_id, sender.get_address(), query,
                                 query_fee, query_ttl_type, query_ttl_value,
                                 response_ttl_type, response_ttl_value,
                                 fee, ttl, nonce
                                 )
        # sign the transaction
        tx_signed, sg, tx_hash = self.client.sign_transaction(sender, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed, tx_hash)
        # save the query id
        self.id = hashing.oracle_query_id(sender.get_address(), nonce, self.oracle_id)
        # return the transaction
        return tx, tx_signed, sg, tx_hash

    def get_response_object(self):
        # TODO: workaround for dashes in the parameter names
        return self.client.get_oracle_query_by_pubkey_and_query_id(**{"pubkey": self.oracle_id, "query-id": self.id})


class Oracle():
    """

    """

    def __init__(self, client, oracle_id=None):
        self.client = client
        self.id = oracle_id
        self.query_id = None

    def register(self, account, query_format, response_format,
                 query_fee=config.ORACLE_DEFAULT_QUERY_FEE,
                 ttl_type=config.ORACLE_DEFAULT_TTL_TYPE_DELTA,
                 ttl_value=config.ORACLE_DEFAULT_TTL_VALUE,
                 vm_version=config.ORACLE_DEFAULT_VM_VERSION,
                 fee=config.DEFAULT_FEE,
                 tx_ttl=config.DEFAULT_TX_TTL):
        """
        Execute a registration of an oracle
        """
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create spend_tx
        tx = txb.tx_oracle_register(
            account.get_address(),
            query_format, response_format,
            query_fee, ttl_type, ttl_value,
            vm_version, fee, ttl, nonce
        )
        # sign the transaction
        tx_signed, sg, tx_hash = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed, tx_hash)
        # register the oracle id
        # the oracle id is the account that register the oracle
        # with the prefix substituted by with ok_
        self.id = f"ok_{account.get_address()[3:]}"
        # return the transaction
        return tx, tx_signed, sg, tx_hash

    def respond(self, account, query_id, response,
                response_ttl_type=config.ORACLE_DEFAULT_TTL_TYPE_DELTA,
                response_ttl_value=config.ORACLE_DEFAULT_RESPONSE_TTL_VALUE,
                fee=config.DEFAULT_FEE,
                tx_ttl=config.DEFAULT_TX_TTL):
        """
        Post a response to an oracle query
        """
        if self.id is None:
            raise ValueError("Oracle id must be provided before respond to a query")
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create spend_tx
        tx = txb.tx_oracle_respond(self.id, query_id, response,
                                   response_ttl_type, response_ttl_value,
                                   fee, ttl, nonce
                                   )
        # sign the transaction
        tx_signed, sg, tx_hash = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed, tx_hash)
        # return the transaction
        return tx, tx_signed, sg, tx_hash

    def extend(self, account, query_id, response,
               ttl_type=config.ORACLE_DEFAULT_TTL_TYPE_DELTA,
               ttl_value=config.ORACLE_DEFAULT_TTL_VALUE,
               fee=config.DEFAULT_FEE,
               tx_ttl=config.DEFAULT_TX_TTL):
        """
        Extend the ttl of an oracle
        """
        if self.id is None:
            raise ValueError("Oracle id must be provided before exending")
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create spend_tx
        tx = txb.tx_oracle_extend(self.id, ttl_type, ttl_value, fee, ttl, nonce)
        # sign the transaction
        tx_signed, sg, tx_hash = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed, tx_hash)
        # return the transaction
        return tx, tx_signed, sg, tx_hash
