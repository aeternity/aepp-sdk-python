import logging
import time
import random
from collections import namedtuple

from aeternity.transactions import TxSigner
from aeternity.signing import Account
from aeternity.openapi import OpenAPIClientException
from aeternity.exceptions import NameNotAvailable, InsufficientFundsException
from aeternity.exceptions import TransactionHashMismatch, TransactionWaitTimeoutExpired, TransactionNotFoundException
from aeternity import config, aens, openapi, transactions, contract, oracles


logger = logging.getLogger(__name__)
logging.root.setLevel(logging.DEBUG)


class EpochRequestError(Exception):
    pass


class EpochClient:

    exception_by_reason = {
        'Name not found': NameNotAvailable,
        'No funds in account': InsufficientFundsException,
        'Transaction not found': TransactionNotFoundException,
    }

    def __init__(self, configs=None, blocking_mode=False, retry=True, debug=False, native=True, offline=False):
        if configs is None:
            configs = config.Config.get_defaults()
        if isinstance(configs, config.Config):
            configs = [configs]
        self._configs = configs
        self._active_config_idx = 0
        self._top_block = None
        self._retry = retry
        # determine how the transaction are going to be created
        # if running offline they are forced to be native
        self.native = native if not offline else True
        # shall the client work in blocking mode
        self.blocking_mode = blocking_mode if not offline else False
        self.offline = offline
        # instantiate the api client
        self.api = None if offline else openapi.OpenAPICli(configs[0].api_url, configs[0].api_url_internal, debug=debug)
        # instantiate the transaction builder object
        self.tx_builder = transactions.TxBuilder(native=self.native, api=self.api)

    def set_native(self, build_native_transactions: bool):
        prev_status = self.native
        self.native = build_native_transactions
        self.tx_builder.native_transactions = build_native_transactions
        return prev_status

    # enable composition
    def __getattr__(self, attr):
        return getattr(self.api, attr)

    def _get_active_config(self):
        return self._configs[self._active_config_idx]

    def _use_next_config(self):
        self._active_config_idx = (self._active_config_idx) + 1 % len(self._configs)

    def update_top_block(self):
        self._top_block = self.get_top_block()

    def compute_absolute_ttl(self, relative_ttl):
        """
        Compute the absolute ttl by adding the ttl to the current height of the chain
        :param relative_ttl: the relative ttl, must be > 0
        """
        if relative_ttl <= 0:
            raise ValueError("ttl must be greater than 0")
        height = self.get_current_key_block_height()
        return height + relative_ttl

    def get_next_nonce(self, account_address):
        """
        Get the next nonce to be used for a transaction for an account
        :param epoch: the epoch client
        :return: the next nonce for an account
        """
        try:
            account = self.api.get_account_by_pubkey(pubkey=account_address)
            return account.nonce + 1
        except Exception as e:
            return 1

    def _get_nonce_ttl(self, account_address: str, relative_ttl: int):
        """
        Helper method to compute both ttl and nonce for an account
        :return: (nonce, ttl)
        """
        ttl = self.compute_absolute_ttl(relative_ttl)
        nonce = self.get_next_nonce(account_address)
        return nonce, ttl

    def get_top_block(self):
        """
        Override the native method to transform the get top block response object
        to a Block
        """
        b = self.api.get_top_block()
        if hasattr(b, 'key_block'):
            return namedtuple('Block', sorted(b.key_block))(**b.key_block)
        else:
            return namedtuple('Block', sorted(b.micro_block))(**b.micro_block)

    def get_block_by_hash(self, hash=None):
        """
        Retrieve a key block or a micro block header
        based on the block hash_prefix
        :param block_hash: either a key block or micro block hash
        :return: the block matching the hash
        """
        block = None
        if hash is None:
            return block
        if hash.startswith("kh_"):
            # key block
            block = self.api.get_key_block_by_hash(hash=hash)
        elif hash.startswith("mh_"):
            # micro block
            block = self.api.get_micro_block_header_by_hash(hash=hash)
        return block

    def broadcast_transaction(self, tx, tx_hash=None):
        """
        Post a transaction to the chain and verify that the hash match the local calculated hash
        It blocks for a period of time to wait for the transaction to be included if in blocking_mode
        """
        reply = self.post_transaction(body={"tx": tx})
        if tx_hash is not None and reply.tx_hash != tx_hash:
            raise TransactionHashMismatch(f"Transaction hash doesn't match, expected {tx_hash} got {reply.tx_hash}")

        if self.blocking_mode:
            self.wait_for_transaction(reply.tx_hash)
        return reply.tx_hash

    def sign_transaction(self, account: Account, tx: str) -> (str, str, str):
        """
        Sign and broadcast a transaction if conditions are met
        Conditions are
        - account is not None
        - operation mode is not offline
        """
        s = TxSigner(account, self._get_active_config().network_id)
        tx_signed, signature, tx_hash = s.sign_encode_transaction(tx)

        return tx_signed, signature, tx_hash

    def spend(self, account: Account, recipient_id, amount, payload="", fee=config.DEFAULT_FEE, tx_ttl=config.DEFAULT_TX_TTL):
        """
        Create and execute a spend transaction
        """
        # retrieve the nonce and ttl
        nonce, tx_ttl = self._get_nonce_ttl(account.get_address(), tx_ttl)
        # build the transaction
        tx = self.tx_builder.tx_spend(account.get_address(), recipient_id, amount, payload, fee, tx_ttl, nonce)
        # execute the transaction
        tx_signed, signature, tx_hash = self.sign_transaction(account, tx)
        # post the transaction
        self.broadcast_transaction(tx_signed, tx_hash=tx_hash)
        return tx, tx_signed, signature, tx_hash

    def wait_for_transaction(self, tx_hash, max_retries=config.MAX_RETRIES, polling_interval=config.POLLING_INTERVAL):
        """
        Wait for a transaction to be mined for an account
        The method will wait for a specific transaction to be included in the chain,
        it will return False if one of the following conditions are met:
        - the chain reply with a 404 not found (the transaction was expunged)
        - the account nonce is >= of the transaction nonce (transaction is in an illegal state)
        - the ttl of the transaction or the one passed as parameter has been reached
        :return: True if the transaction id found False otherwise
        """
        if max_retries <= 0:
            raise ValueError("Retries must be greater than 0")

        n = 1
        total_sleep = 0
        while True:
            # query the transaction
            try:
                tx = self.get_transaction_by_hash(hash=tx_hash)
                # get the account nonce
            except OpenAPIClientException as e:
                # it may fail because it is not found that means that
                # or it was invalid or the ttl has expired
                raise TransactionWaitTimeoutExpired(tx_hash=tx_hash, reason=e.reason)
            # if the tx.block_height > 0 we win
            if tx.block_height > 0:
                break
            if n >= max_retries:
                raise TransactionWaitTimeoutExpired(tx_hash=tx_hash, reason=f"The transaction was not included in {total_sleep} seconds, wait aborted")
            # calculate sleep time
            sleep_time = (polling_interval ** n) + (random.randint(0, 1000) / 1000.0)
            time.sleep(sleep_time)
            total_sleep += sleep_time
            # increment n
            n += 1

    # support naming
    def AEName(self, domain):
        return aens.AEName(domain, client=self)

    # support contract
    def Contract(self, source_code, bytecode=None, address=None, abi=contract.Contract.SOPHIA):
        return contract.Contract(source_code, client=self, bytecode=bytecode, address=address, abi=abi)

    # support oralces
    def Oracle(self):
        return oracles.Oracle(self)

    def OracleQuery(self, oracle_id, query_id=None):
        return oracles.OracleQuery(self, oracle_id, id=query_id)
