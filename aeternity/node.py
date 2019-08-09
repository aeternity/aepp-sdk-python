import logging
import time
import random
from datetime import datetime, timedelta
import namedtupled

from aeternity.transactions import TxSigner
from aeternity.signing import Account
from aeternity.openapi import OpenAPIClientException
from aeternity import aens, openapi, transactions, contract, oracles, defaults, identifiers, exceptions, utils
from aeternity.exceptions import TransactionWaitTimeoutExpired, TransactionHashMismatch
from aeternity import __node_compatibility__

logger = logging.getLogger(__name__)
logging.root.setLevel(logging.DEBUG)


class Config:
    def __init__(self,
                 external_url='http://localhost:3013',
                 internal_url='http://localhost:3113',
                 websocket_url='http://localhost:3014',
                 force_compatibility=False,
                 **kwargs):
        """
        :param external_url: the node external url
        :param internal_url: the node internal url
        :param websocket_url: the node websocket url
        :param blocking_mode: block the client waiting for transactions (default False)
        :param native: build transaction natively (do not use the node internal endpoints) (default True)
        :param force_compatibility: ignore node version compatibility check (default False)
        :param debug: enable debug logging (default False)
        """
        # endpoint urls
        self.api_url = external_url
        self.api_url_internal = internal_url
        self.websocket_url = websocket_url
        self.force_compatibility = force_compatibility
        self.blocking_mode = kwargs.get("blocking_mode", False)
        # defaults # TODO: pass defaults to the tx builder
        self.tx_gas_per_byte = kwargs.get("tx_gas_per_byte", defaults.GAS_PER_BYTE)
        self.tx_base_gas = kwargs.get("tx_base_gas", defaults.BASE_GAS)
        self.tx_gas_price = kwargs.get("tx_gas_price", defaults.GAS_PRICE)
        # get the version
        self.network_id = kwargs.get("network_id", None)
        # contracts defaults
        self.contract_gas = kwargs.get("contract_gas", defaults.CONTRACT_GAS)
        self.contract_gas_price = kwargs.get("contract_gas_price", defaults.CONTRACT_GAS_PRICE)
        # oracles default
        self.orcale_ttl_type = kwargs.get("oracle_ttl_type", defaults.ORACLE_TTL_TYPE)
        # chain defaults
        self.key_block_interval = kwargs.get("key_block_interval", defaults.KEY_BLOCK_INTERVAL)
        self.key_block_confirmation_num = kwargs.get("key_block_confirmation_num", defaults.KEY_BLOCK_CONFIRMATION_NUM)
        # tuning
        self.poll_tx_max_retries = kwargs.get("poll_tx_max_retries", defaults.POLL_TX_MAX_RETRIES)
        self.poll_tx_retries_interval = kwargs.get("poll_tx_retries_interval", defaults.POLL_TX_RETRIES_INTERVAL)
        self.poll_block_max_retries = kwargs.get("poll_block_max_retries", defaults.POLL_BLOCK_MAX_RETRIES)
        self.poll_block_retries_interval = kwargs.get("poll_block_retries_interval", defaults.POLL_BLOCK_RETRIES_INTERVAL)
        # debug
        self.debug = kwargs.get("debug", False)

    def __str__(self):
        return f'ws:{self.websocket_url} ext:{self.api_url} int:{self.api_url_internal}'


class NodeClient:

    def __init__(self, config=Config()):
        """
        Initialize a new EpochClient
        :param config: the configuration to use or empty for default (default None)
        """
        self.config = config
        # determine how the transaction are going to be created
        # if running offline they are forced to be native
        # shall the client work in blocking mode
        # instantiate the api client
        self.api = openapi.OpenAPICli(url=config.api_url,
                                      url_internal=config.api_url_internal,
                                      debug=config.debug,
                                      force_compatibility=config.force_compatibility,
                                      compatibility_version_range=__node_compatibility__)
        # instantiate the transaction builder object
        self.tx_builder = transactions.TxBuilder()
        # network id
        if self.config.network_id is None:
            self.config.network_id = self.api.get_status().network_id

    # enable composition
    def __getattr__(self, attr):
        return getattr(self.api, attr)

    def compute_absolute_ttl(self, relative_ttl):
        """
        Compute the absolute ttl by adding the ttl to the current height of the chain
        :param relative_ttl: the relative ttl, if 0 will set the ttl to 0
        """
        ttl = dict(
            absolute_ttl=0,
            height=self.get_current_key_block_height(),
            estimated_expiration=datetime.now()
        )
        if relative_ttl > 0:
            ttl["absolute_ttl"] = ttl["height"] + relative_ttl
            ttl["estimated_expiration"] = datetime.now() + timedelta(minutes=self.config.key_block_interval * relative_ttl)
        return namedtupled.map(ttl, _nt_name="TTL")

    def get_next_nonce(self, account_address):
        """
        Get the next nonce to be used for a transaction for an account
        :param node: the node client
        :return: the next nonce for an account
        """
        try:
            account = self.api.get_account_by_pubkey(pubkey=account_address)
            return account.nonce + 1
        except Exception:
            return 1

    def _get_nonce_ttl(self, account_address: str, relative_ttl: int):
        """
        Helper method to compute both absolute ttl and  nonce for an account
        :return: (nonce, ttl)
        """
        ttl = self.compute_absolute_ttl(relative_ttl).absolute_ttl if relative_ttl > 0 else 0
        nonce = self.get_next_nonce(account_address)
        return nonce, ttl

    def get_top_block(self):
        """
        Override the native method to transform the get top block response object
        to a Block
        """
        b = self.api.get_top_block()
        return b.key_block if hasattr(b, 'key_block') else b.micro_block

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
        if hash.startswith(f"{identifiers.KEY_BLOCK_HASH}_"):
            # key block
            block = self.api.get_key_block_by_hash(hash=hash)
        elif hash.startswith(f"{identifiers.MICRO_BLOCK_HASH}_"):
            # micro block
            block = self.api.get_micro_block_header_by_hash(hash=hash)
        return block

    def broadcast_transaction(self, tx, tx_hash=None):
        """
        Post a transaction to the chain and verify that the hash match the local calculated hash
        It blocks for a period of time to wait for the transaction to be included if in blocking_mode
        """
        tx = tx.tx if hasattr(tx, "tx") else tx
        reply = self.post_transaction(body={"tx": tx})
        if tx_hash is not None and reply.tx_hash != tx_hash:
            raise TransactionHashMismatch(f"Transaction hash doesn't match, expected {tx_hash} got {reply.tx_hash}")

        if self.config.blocking_mode:
            self.wait_for_transaction(reply.tx_hash)
        return reply.tx_hash

    def sign_transaction(self, account: Account, tx: object, metadata: dict = None, **kwargs) -> tuple:
        """
        Sign a transaction
        :return: the transaction for the transaction
        """
        # first retrieve the account from the node
        # so we can check if it is generalized or not
        on_chain_account = self.get_account(account.get_address())

        # if the account is not generalized sign and return the transaction
        if not on_chain_account.is_generalized():
            s = TxSigner(account, self.config.network_id)
            return s.sign_encode_transaction(tx, metadata)

        # if the account is generalized then prepare the ga_meta_tx
        # 1. wrap the tx into a sigend tx (without signatures)
        sg_tx = self.tx_builder.tx_signed([], tx)
        # 2. wrap the tx into a ga_meta_tx
        # get the absolute ttl
        ttl = self.compute_absolute_ttl(kwargs.get("ttl", defaults.TX_TTL)).absolute_ttl
        # get abi version
        _, abi = self.get_vm_abi_versions()
        # check that the parameter auth_data is provided
        auth_data = kwargs.get("auth_data")
        if auth_data is None:
            raise TypeError("the auth_data parameter is required for ga accounts")
        # verify the gas amount TODO: add a tx verification
        gas = kwargs.get("gas", defaults.GA_MAX_AUTH_FUN_GAS)
        if gas > defaults.GA_MAX_AUTH_FUN_GAS:
            raise TypeError(f"the maximum gas value for ga auth_fun is {defaults.GA_MAX_AUTH_FUN_GAS}, got {gas}")
        # build the
        ga_sg_tx = self.tx_builder.tx_ga_meta(
            account.get_address(),
            auth_data,
            kwargs.get("abi_version", abi),
            kwargs.get("fee", defaults.FEE),
            gas,
            kwargs.get("gas_price", defaults.CONTRACT_GAS_PRICE),
            ttl,
            sg_tx
        )
        # 3. wrap the the ga into a signed transaction
        sg_ga_sg_tx = self.tx_builder.tx_signed([], ga_sg_tx)
        return sg_ga_sg_tx

    def get_account(self, address: str) -> Account:
        """
        Retrieve an account by it's public key
        """
        if not utils.is_valid_hash(address, identifiers.ACCOUNT_ID):
            raise TypeError(f"Input {address} is not a valid aeternity address")
        remote_account = self.get_account_by_pubkey(pubkey=address)
        return Account.from_node_api(remote_account)

    def spend(self, account: Account,
              recipient_id: str,
              amount: int,
              payload: str = "",
              fee: int = defaults.FEE,
              tx_ttl: int = defaults.TX_TTL):
        """
        Create and execute a spend transaction
        """
        # retrieve the nonce
        account.nonce = self.get_next_nonce(account.get_address()) if account.nonce == 0 else account.nonce + 1
        # retrieve ttl
        tx_ttl = self.compute_absolute_ttl(tx_ttl)
        # build the transaction
        tx = self.tx_builder.tx_spend(account.get_address(), recipient_id, amount, payload, fee, tx_ttl.absolute_ttl, account.nonce)
        # execute the transaction
        tx = self.sign_transaction(account, tx.tx)
        # post the transaction
        self.broadcast_transaction(tx.tx, tx_hash=tx.hash)
        return tx

    def wait_for_transaction(self, tx_hash, max_retries=None, polling_interval=None, confirm_transaction=False):
        """
        Wait for a transaction to be mined for an account
        The method will wait for a specific transaction to be included in the chain,
        it will return False if one of the following conditions are met:
        - the chain reply with a 404 not found (the transaction was expunged)
        - the account nonce is >= of the transaction nonce (transaction is in an illegal state)
        - the ttl of the transaction or the one passed as parameter has been reached
        :return: the block height of the transaction if it has been found

        Raises TransactionWaitTimeoutExpired if the transaction hasnt been found
        """

        retries = max_retries if max_retries is not None else self.config.poll_tx_max_retries
        interval = polling_interval if polling_interval is not None else self.config.poll_tx_retries_interval
        if retries <= 0:
            raise ValueError("Retries must be greater than 0")

        # start polling
        n = 1
        total_sleep = 0
        tx_height = -1
        while True:
            # query the transaction
            try:
                tx = self.get_transaction_by_hash(hash=tx_hash)
                # get the account nonce
            except OpenAPIClientException as e:
                # it may fail because it is not found that means that
                # or it was invalid or the ttl has expired
                reason = e.reason if hasattr(e, "reason") else "Timeout expired"
                raise TransactionWaitTimeoutExpired(tx_hash=tx_hash, reason=reason)
            # if the tx.block_height >= min_block_height we are ok
            if tx.block_height >= 0:
                tx_height = tx.block_height
                break
            if n >= retries:
                raise TransactionWaitTimeoutExpired(tx_hash=tx_hash, reason=f"The transaction was not included in {total_sleep} seconds, wait aborted")
            # calculate sleep time
            sleep_time = (interval ** n) + (random.randint(0, 1000) / 1000.0)
            time.sleep(sleep_time)
            total_sleep += sleep_time
            # increment n
            n += 1
        return tx_height

    def wait_for_confirmation(self, tx_hash, max_retries=None, polling_interval=None):
        """
        Wait for a transaction to be confirmed by at least "key_block_confirmation_num" blocks (default 3)
        The amount of blocks can be configured in the Config object using key_block_confirmation_num parameter
        """
        # first wait for the transaction to be found
        tx_height = self.wait_for_transaction(tx_hash)
        # now calculate the min block height
        min_block_height = tx_height + self.config.key_block_confirmation_num
        # get teh
        retries = max_retries if max_retries is not None else self.config.poll_block_max_retries
        interval = polling_interval if polling_interval is not None else self.config.poll_block_retries_interval
        if retries <= 0 or interval <= 0:
            raise ValueError("max_retries and polling_interval must be greater than 0")
        # start polling
        n = 1
        total_sleep = 0
        while True:
            current_height = self.get_current_key_block_height()
            # if the tx.block_height >= min_block_height we are ok
            if current_height >= min_block_height:
                break
            if n >= retries:
                raise TransactionWaitTimeoutExpired(tx_hash=tx_hash, reason=f"The transaction was not included in {total_sleep} seconds, wait aborted")
            # calculate sleep time
            time.sleep(interval)
            total_sleep += interval
            # increment n
            n += 1

    def transfer_funds(self, account: Account,
                       recipient_id: str,
                       percentage: float,
                       payload: str = "",
                       tx_ttl: int = defaults.TX_TTL,
                       include_fee=True):
        """
        Create and execute a spend transaction
        """
        if percentage < 0 or percentage > 1:
            raise ValueError(f"Percentage should be a number between 0 and 1, got {percentage}")
        account_on_chain = self.get_account_by_pubkey(pubkey=account.get_address())
        request_transfer_amount = int(account_on_chain.balance * percentage)
        # retrieve the nonce
        account.nonce = account_on_chain.nonce + 1
        # retrieve ttl
        tx_ttl = self.compute_absolute_ttl(tx_ttl)
        # build the transaction
        tx = self.tx_builder.tx_spend(account.get_address(), recipient_id, request_transfer_amount, payload, defaults.FEE, tx_ttl.absolute_ttl, account.nonce)
        # if the request_transfer_amount should include the fee keep calculating the fee
        if include_fee:
            amount = request_transfer_amount
            while (amount + tx.data.fee) > request_transfer_amount:
                amount = request_transfer_amount - tx.data.fee
                tx = self.tx_builder.tx_spend(account.get_address(), recipient_id, amount, payload, defaults.FEE, tx_ttl.absolute_ttl, account.nonce)
        # execute the transaction
        tx = self.sign_transaction(account, tx.tx)
        # post the transaction
        self.broadcast_transaction(tx.tx, tx_hash=tx.hash)
        return tx

    def get_consensus_protocol_version(self, height: int = None) -> int:
        """
        Get the consensus protocol version number
        :param height: the height to get the protocol version for, if None the current height will be used
        :return: the version
        """
        if height is None:
            height = self.get_current_key_block_height()
        if height < 0:
            raise ValueError("height must be a number >= 0")
        status = self.get_status()
        effective_at_height = -1
        version = 0
        for p in status.protocols:
            if height >= p.effective_at_height and p.effective_at_height > effective_at_height:
                version, effective_at_height = p.version, p.effective_at_height
        return version

    def verify(self, encoded_tx):
        """
        Unpack and verify an encoded transaction
        """
        decoded = transactions._tx_native(transactions.UNPACK_TX, tx=encoded_tx)
        return decoded

    def get_vm_abi_versions(self):
        """
        Check the version of the node and retrieve the correct values for abi and vm version
        """
        protocol_version = self.get_consensus_protocol_version()
        protocol_abi_vm = identifiers.PROTOCOL_ABI_VM.get(protocol_version)
        if protocol_abi_vm is None:
            raise exceptions.UnsupportedNodeVersion(f"Version {self.api_version} is not supported")
        return (protocol_abi_vm.get("vm"), protocol_abi_vm.get("abi"))

    def account_basic_to_ga(self, account: Account, ga_contract: str,
                            init_calldata: str = defaults.CONTRACT_INIT_CALLDATA,
                            auth_fun: str = defaults.GA_AUTH_FUNCTION,
                            fee: int = defaults.FEE,
                            tx_ttl: int = defaults.TX_TTL,
                            gas: int = defaults.CONTRACT_GAS,
                            gas_price: int = defaults.CONTRACT_GAS_PRICE):
        """
        Transform a POA (Plain Old Account) to a GA (Generalized Account)
        :param account: the account to transform
        :param contract: the compiled contract associated to the GA
        :param auth_fun: the name of the contract function to use for authorization (default: authorize)
        """
        # check the auth_fun name
        if auth_fun is None or len(auth_fun) == 0:
            raise TypeError("The parameter auth_fun is required")
        # decode the contract and search for the authorization function
        auth_fun_hash = None
        contract_data = contract.CompilerClient.decode_bytecode(ga_contract)
        for ti in contract_data.type_info:
            if ti.fun_name == auth_fun:
                auth_fun_hash = ti.fun_hash
        # if the function is not found then raise an error
        if auth_fun_hash is None:
            raise TypeError(f"Authorization function not found: '{auth_fun}'")
        # get the nonce
        nonce = self.get_next_nonce(account.get_address())
        # compute the ttl
        ttl = self.compute_absolute_ttl(tx_ttl).absolute_ttl
        # get abi and vm version
        vm_version, abi_version = self.get_vm_abi_versions()
        # build the transaction
        tx = self.tx_builder.tx_ga_attach(
            account.get_address(),
            nonce,
            ga_contract,
            auth_fun_hash,
            vm_version,
            abi_version,
            fee,
            ttl,
            gas,
            gas_price,
            init_calldata
        )
        # sign the transaction
        tx = self.sign_transaction(account, tx)
        # broadcast the transaction
        self.broadcast_transaction(tx, tx_hash=tx.hash)
        return tx

    # support naming
    def AEName(self, domain):
        return aens.AEName(domain, client=self)

    # support oracles
    def Oracle(self):
        return oracles.Oracle(self)

    def OracleQuery(self, oracle_id, query_id=None):
        return oracles.OracleQuery(self, oracle_id, id=query_id)

    # support contract
    def Contract(self):
        return contract.Contract(client=self)
