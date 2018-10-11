from aeternity.aevm import pretty_bytecode
from aeternity.openapi import OpenAPIClientException
from aeternity.transactions import TxBuilder
from aeternity import utils, epoch
from aeternity.config import DEFAULT_TX_TTL, DEFAULT_FEE
from aeternity.config import CONTRACT_DEFAULT_GAS, CONTRACT_DEFAULT_GAS_PRICE, CONTRACT_DEFAULT_VM_VERSION, CONTRACT_DEFAULT_DEPOSIT


class ContractError(Exception):
    pass


# contract lifecycle is
# compile contract (get the bytecode)
# deploy the contract (get the address)
# encode the calldata (get the )


class Contract:
    EVM = 'evm'
    SOPHIA = 'sophia'

    def __init__(self, source_code, bytecode=None, address=None, abi=SOPHIA, client=None):
        """
        Initialize a contract object

        if bytecode is not provided it will be computed using the compile command.

        :param source_code: the source code of the contract
        :param bytecode: the bytecode of the contract
        :param address: the address of the contract
        :param abi: the abi, default 'sofia'
        :param client: the epoch client to use
        """
        if client is None:
            client = epoch.EpochClient()
        self.client = client
        self.abi = abi
        self.source_code = source_code
        self.bytecode = bytecode
        self.address = address
        if self.bytecode is None:
            self.bytecode = self.compile(self.source_code)

    def tx_call(self, keypair, function, arg,
                amount=10,
                gas=CONTRACT_DEFAULT_GAS,
                gas_price=CONTRACT_DEFAULT_GAS_PRICE,
                fee=DEFAULT_FEE,
                vm_version=CONTRACT_DEFAULT_VM_VERSION,
                tx_ttl=DEFAULT_TX_TTL):
        """Call a sophia contract"""

        if not utils.is_valid_hash(self.address, prefix="ct"):
            raise ValueError("Missing contract id")

        try:
            call_data = self.encode_calldata(function, arg)
            txb = TxBuilder(self.client, keypair)
            tx, sg, tx_hash = txb.tx_contract_call(self.address, call_data, function, arg, amount, gas, gas_price, vm_version, fee, tx_ttl)
            # post the transaction to the chain
            txb.post_transaction(tx, tx_hash)
            # wait for transaction to be mined
            txb.wait_tx(tx_hash)
            # unsigned transaction of the call
            call_obj = self.client.cli.get_transaction_info_by_hash(hash=tx_hash)
            return call_obj
        except OpenAPIClientException as e:
            raise ContractError(e)

    def tx_create(self,
                  keypair,
                  amount=1,
                  deposit=CONTRACT_DEFAULT_DEPOSIT,
                  init_state="()",
                  gas=CONTRACT_DEFAULT_GAS,
                  gas_price=CONTRACT_DEFAULT_GAS_PRICE,
                  fee=DEFAULT_FEE,
                  vm_version=CONTRACT_DEFAULT_VM_VERSION,
                  tx_ttl=DEFAULT_TX_TTL):
        """
        Create a contract and deploy it to the chain
        :return: address
        """
        try:
            call_data = self.encode_calldata("init", init_state)

            # get the transaction builder
            txb = TxBuilder(self.client, keypair)
            # create spend_tx
            tx, sg, tx_hash, contract_id = txb.tx_contract_create(self.bytecode, call_data, amount, deposit, gas, gas_price, vm_version, fee, tx_ttl)
            # post the transaction to the chain
            txb.post_transaction(tx, tx_hash)
            if self.client.blocking_mode:
                txb.wait_tx(tx_hash)
            # store the contract address in the instance variabl
            self.address = contract_id
            return tx
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
            data = self.client.cli.compile_contract(body=dict(
                code=code,
                options=options
            ))
            return data.bytecode
        except OpenAPIClientException as e:
            raise ContractError(e)

    def get_pretty_bytecode(self, code, options=''):
        return pretty_bytecode(self.bytecode)

    def call(self, function, arg):
        '''"Call a sophia function with a given name and argument in the given
        bytecode off chain.'''
        try:
            # see: /epoch/lib/aehttp-0.1.0/src/aehttp_dispatch_ext.erl
            data = self.client.cli.call_contract(body=dict(
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
            data = self.client.cli.encode_calldata(body=dict(
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
            reply = self.client.cli.decode_data(body={
                "data": data,
                "sophia-type": sophia_type,
            })
            return reply.data.get('value'), reply.data.get('type', 'word')
        except OpenAPIClientException as e:
            raise ContractError(e)
