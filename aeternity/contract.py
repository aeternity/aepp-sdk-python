from aeternity.epoch import EpochClient
from aeternity.aevm import pretty_bytecode
from aeternity.openapi import OpenAPIClientException


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


    def encode_calldata(self, function, arg):
        data = self.client.external_http_post(
            'contract/encode-calldata',
            json={
                'abi': 'evm',
                'code': self.code,
                'function': function,
                'arg': arg,
            }
        )
        error = data.get('reason')
        if error:
            raise ContractError(error)
        return data['calldata']

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
