from aeternity.epoch import EpochClient
from aeternity.aevm import pretty_bytecode
from aeternity.openapi import OpenAPIClientException
from aeternity.config import DEFAULT_TX_TTL, DEFAULT_FEE
from aeternity.config import CONTRACT_DEFAULT_GAS, CONTRACT_DEFAULT_GAS_PRICE, CONTRACT_DEFAULT_VM_VERSION, CONTRACT_DEFAULT_DEPOSIT


class ContractError(Exception):
    pass


# contract lifecicle is
# compile contract (get the bytecode)
# deploy the contract (get the address)
# encode the calldata (get the )
class Contract:
    EVM = 'evm'
    SOPHIA = 'sophia'

    def __init__(self, contract_source, abi=SOPHIA, client=None, contract_bytecode=None):
        if client is None:
            client = EpochClient()
        self.client = client
        self.contract_source = contract_source
        self.contract_bytecode = contract_bytecode
        if self.contract_bytecode is None:
            self.contract_bytecode = self.compile(self.contract_source)
        self.abi = abi

    def tx_call(self, contract_address, keypair, function, arg,
                amount=10,
                gas=CONTRACT_DEFAULT_GAS,
                gas_price=CONTRACT_DEFAULT_GAS_PRICE,
                fee=DEFAULT_FEE,
                vm_version=CONTRACT_DEFAULT_VM_VERSION,
                tx_ttl=DEFAULT_TX_TTL):
        """Call a sophia contract"""
        call_data = self.encode_calldata(function, arg, abi=self.SOPHIA)
        try:
            ttl = self.client.compute_absolute_ttl(tx_ttl)
            contract_reply = self.client.cli.post_contract_call(body=dict(
                call_data=call_data,
                caller=keypair.get_address(),
                contract=contract_address,
                amount=amount,
                fee=fee,
                gas=gas,
                gas_price=gas_price,
                vm_version=vm_version,
                ttl=ttl
            ))
            # post transaction
            signed_tx = self.client.post_transaction(keypair, contract_reply)
            # wait for transcation to be mined
            self.client.wait_for_next_block()
            # unsigend transaciton of the call
            call_obj = self.client.cli.get_contract_call_from_tx(tx_hash=signed_tx.tx_hash)
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
        :return: contract_address
        """
        try:
            ttl = self.client.compute_absolute_ttl(tx_ttl)
            call_data = self.encode_calldata("init", init_state, abi=self.SOPHIA)
            contract_transaction = self.client.cli.post_contract_create(body=dict(
                owner=keypair.get_address(),
                amount=amount,
                deposit=deposit,
                fee=fee,
                gas=gas,
                gas_price=gas_price,
                vm_version=vm_version,
                call_data=call_data,
                code=self.contract_bytecode,
                ttl=ttl
            ))
            tx = self.client.post_transaction(keypair, contract_transaction)
            return contract_transaction.contract_address, tx
        except OpenAPIClientException as e:
            raise ContractError(e)

    def tx_create_wait(self, keypair,
                       amount=1,
                       deposit=CONTRACT_DEFAULT_DEPOSIT,
                       init_state="()",
                       gas=CONTRACT_DEFAULT_GAS,
                       gas_price=CONTRACT_DEFAULT_GAS_PRICE,
                       fee=DEFAULT_FEE,
                       vm_version=CONTRACT_DEFAULT_VM_VERSION,
                       tx_ttl=DEFAULT_TX_TTL):
        c, tx = self.tx_create(keypair, amount, deposit, init_state, gas, gas_price, fee, vm_version, tx_ttl)
        self.client.wait_for_next_block()
        return c, tx

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
        return pretty_bytecode(self.contract_bytecode)

    def call(self, function, arg):
        '''"Call a sophia function with a given name and argument in the given
        bytecode off chain.'''
        try:
            # see: /epoch/lib/aehttp-0.1.0/src/aehttp_dispatch_ext.erl
            data = self.client.cli.call_contract(body=dict(
                code=self.contract_bytecode,
                function=function,
                arg=arg,
                abi=self.abi,
            ))
            return data
        except OpenAPIClientException as e:
            raise ContractError(e)

    def encode_calldata(self, function, arg, abi=SOPHIA):
        """
        Encode the function and arguments of a contract call.
        """
        try:
            data = self.client.cli.encode_calldata(body=dict(
                abi=abi,
                code=self.contract_bytecode,
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
