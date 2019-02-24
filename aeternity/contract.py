from aeternity.openapi import OpenAPIClientException, UnsupportedEpochVersion
from aeternity import utils, config
from aeternity.identifiers import CONTRACT_ID, CONTRACT_ROMA_VM, CONTRACT_ROMA_ABI, CONTRACT_MINERVA_VM, CONTRACT_MINERVA_ABI
import semver


class ContractError(Exception):
    pass


# contract lifecycle is
# compile contract (get the bytecode)
# deploy the contract (get the address)
# encode the calldata (get the )


class Contract:
    EVM = 'evm'
    SOPHIA = 'sophia'

    def __init__(self, source_code, client, bytecode=None, address=None, abi=SOPHIA):
        """
        Initialize a contract object

        if bytecode is not provided it will be computed using the compile command.

        :param source_code: the source code of the contract
        :param bytecode: the bytecode of the contract
        :param address: the address of the contract
        :param abi: the abi, default 'sophia'
        :param client: the epoch client to use
        """
        self.client = client
        self.abi = abi
        self.source_code = source_code
        self.bytecode = bytecode
        self.address = address
        if self.bytecode is None:
            self.bytecode = self.compile(self.source_code)

    def tx_call(self, account, function, arg,
                amount=config.CONTRACT_DEFAULT_AMOUNT,
                gas=config.CONTRACT_DEFAULT_GAS,
                gas_price=config.CONTRACT_DEFAULT_GAS_PRICE,
                fee=config.DEFAULT_FEE,
                vm_version=None,
                abi_version=None,
                tx_ttl=config.DEFAULT_TX_TTL):
        """Call a sophia contract"""

        if not utils.is_valid_hash(self.address, prefix=CONTRACT_ID):
            raise ValueError("Missing contract id")

        try:
            # retrieve the correct vm/abi version
            vm, abi = self._get_vm_abi_versions()
            vm_version = vm if vm_version is None else vm_version
            abi_version = abi if abi_version is None else abi_version
            # prepare the call data
            call_data = self.encode_calldata(function, arg)
            # get the transaction builder
            txb = self.client.tx_builder
            # get the account nonce and ttl
            nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
            # build the transaction
            tx = txb.tx_contract_call(account.get_address(), self.address, call_data, function, arg,
                                      amount, gas, gas_price, abi_version,
                                      fee, ttl, nonce)
            # sign the transaction
            tx_signed, sg, tx_hash = self.client.sign_transaction(account, tx)
            # post the transaction to the chain
            self.client.broadcast_transaction(tx_signed, tx_hash)
            # unsigned transaction of the call
            call_obj = self.client.get_transaction_info_by_hash(hash=tx_hash)
            return tx, tx_signed, sg, tx_hash, call_obj
        except OpenAPIClientException as e:
            raise ContractError(e)

    def tx_create(self,
                  account,
                  amount=config.CONTRACT_DEFAULT_AMOUNT,
                  deposit=config.CONTRACT_DEFAULT_DEPOSIT,
                  init_state="()",
                  gas=config.CONTRACT_DEFAULT_GAS,
                  gas_price=config.CONTRACT_DEFAULT_GAS_PRICE,
                  fee=config.DEFAULT_FEE,
                  vm_version=None,
                  abi_version=None,
                  tx_ttl=config.DEFAULT_TX_TTL):
        """
        Create a contract and deploy it to the chain
        :return: address
        """
        try:
            # retrieve the correct vm/abi version
            vm, abi = self._get_vm_abi_versions()
            vm_version = vm if vm_version is None else vm_version
            abi_version = abi if abi_version is None else abi_version
            # encode the call data
            call_data = self.encode_calldata("init", init_state)
            # get the transaction builder
            txb = self.client.tx_builder
            # get the account nonce and ttl
            nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
            # build the transaction
            tx, contract_id = txb.tx_contract_create(account.get_address(), self.bytecode, call_data,
                                                     amount, deposit, gas, gas_price, vm_version, abi_version,
                                                     fee, ttl, nonce)
            # sign the transaction
            tx_signed, sg, tx_hash = self.client.sign_transaction(account, tx)
            # post the transaction to the chain
            self.client.broadcast_transaction(tx_signed, tx_hash)
            # store the contract address in the instance variabl
            self.address = contract_id
            return tx, tx_signed, sg, tx_hash
        except OpenAPIClientException as e:
            raise ContractError(e)

    def compile(self, code, options=''):
        """
        Compile a sophia contract from source
        :param code: the source code of the the contract
        :param options: additional options for the contract TODO: link the documentation for the options
        :return: the contract bytecode
        """
        try:
            data = self.client.compile_contract(body=dict(
                code=code,
                options=options
            ))
            return data.bytecode
        except OpenAPIClientException as e:
            raise ContractError(e)

    def get_pretty_bytecode(self, code, options=''):
        return self.bytecode

    def call(self, function, arg):
        '''"Call a sophia function with a given name and argument in the given
        bytecode off chain.'''
        try:
            # see: /epoch/lib/aehttp-0.1.0/src/aehttp_dispatch_ext.erl
            data = self.client.call_contract(body=dict(
                code=self.bytecode,
                function=function,
                arg=arg,
                abi=self.abi,
            ))
            return data
        except OpenAPIClientException as e:
            raise ContractError(e)

    def encode_calldata(self, function, arg):
        """
        Encode the function and arguments of a contract call.
        """
        try:
            data = self.client.encode_calldata(body=dict(
                abi=self.abi,
                code=self.bytecode,
                function=function,
                arg=arg,
            ))
            return data.calldata
        except OpenAPIClientException as e:
            raise ContractError(e)

    def decode_data(self, data, sophia_type):
        """
        Decode the result of a contract computation
        :param data: the result returned by a contract execution
        :param sophia_type: the expected type of the result

        :return: a tuple of (value, type)
        """
        try:
            reply = self.client.decode_data(body={
                "data": data,
                "sophia-type": sophia_type,
            })
            return reply.data.value, reply.data.type
        except OpenAPIClientException as e:
            raise ContractError(e)

    def _get_vm_abi_versions(self):
        """
        Check the version of the node and retrieve the correct values for abi and vm version
        """
        if semver.match(self.client.api_version, "<=1.4.0"):
            return CONTRACT_ROMA_VM, CONTRACT_ROMA_ABI
        if semver.match(self.client.api_version, "<3.0.0"):
            return CONTRACT_MINERVA_VM, CONTRACT_MINERVA_ABI
        raise UnsupportedEpochVersion(f"Version {self.client.api_version} is not supported")
