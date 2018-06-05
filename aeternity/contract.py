from aeternity.epoch import EpochClient
from aeternity.aevm import pretty_bytecode
from aeternity.openapi import OpenAPIClientException
from aeternity.config import DEFAULT_TX_TTL, DEFAULT_FEE, CONTRACT_DEFAULT_GAS, CONTRACT_DEFAULT_GAS_PRICE, CONTRACT_DEFAULT_VM_VERSION


class ContractError(Exception):
    pass


class Contract:
    EVM = 'evm'
    SOPHIA = 'sophia'

    def __init__(self, code, abi, client=None):
        if client is None:
            client = EpochClient()
        self.client = client
        self.code = code
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
            return contract_reply
        except OpenAPIClientException as e:
            raise ContractError(e)

    def tx_call_compute(self, contract_address, keypair, function, arg,
                        amount=10,
                        gas=CONTRACT_DEFAULT_GAS,
                        gas_price=CONTRACT_DEFAULT_GAS_PRICE,
                        fee=DEFAULT_FEE,
                        vm_version=CONTRACT_DEFAULT_VM_VERSION,
                        tx_ttl=DEFAULT_TX_TTL):
        """Call a sophia contract (shortcut for tx_call)"""
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
                function=function,
                argument=arg,
                ttl=ttl
            ))
            return contract_reply
        except OpenAPIClientException as e:
            raise ContractError(e)

    def tx_create(self, keypair,
                  amount=1,
                  deposit=10,
                  call_data="",
                  gas=CONTRACT_DEFAULT_GAS,
                  gas_price=CONTRACT_DEFAULT_GAS_PRICE,
                  fee=DEFAULT_FEE,
                  vm_version=CONTRACT_DEFAULT_VM_VERSION,
                  tx_ttl=DEFAULT_TX_TTL):
        """:return: contract_address """
        try:
            ttl = self.client.compute_absolute_ttl(tx_ttl)
            compiled_code = self.compile()
            contract_transaction = self.client.cli.post_contract_create(body=dict(
                owner=keypair.get_address(),
                amount=amount,
                deposit=deposit,
                fee=fee,
                gas=gas,
                gas_price=gas_price,
                vm_version=vm_version,
                call_data=call_data,
                code=compiled_code,
                ttl=ttl
            ))
            tx = self.client.post_transaction(keypair, contract_transaction)
            return contract_transaction.contract_address, tx
        except OpenAPIClientException as e:
            raise ContractError(e)

    def compile(self, options=''):
        """Compile a sophia contract from source and return byte code"""
        try:
            data = self.client.cli.compile_contract(body=dict(
                code=self.code,
                options=options
            ))
            return data.bytecode
        except OpenAPIClientException as e:
            raise ContractError(e)

    def get_pretty_bytecode(self, options=''):
        bytecode = self.compile(options=options)
        return pretty_bytecode(bytecode)

    def call(self, function, arg):
        '''"Call a sophia function with a given name and argument in the given
        bytecode off chain.'''

        compiled_code = self.compile()
        try:
            # see: /epoch/lib/aehttp-0.1.0/src/aehttp_dispatch_ext.erl
            data = self.client.cli.call_contract(body=dict(
                code=compiled_code,
                function=function,
                arg=arg,
                abi=self.abi,
            ))
            return data
        except OpenAPIClientException as e:
            raise ContractError(e)

    def encode_calldata(self, function, arg, abi=EVM):
        try:
            data = self.client.cli.encode_calldata(body=dict(
                abi=abi,
                code=self.code,
                function=function,
                arg=arg,
            ))
            return data.calldata
        except OpenAPIClientException as e:
            raise ContractError(e)
