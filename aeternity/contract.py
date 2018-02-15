import json

import binascii


class ContractError(Exception):
    pass


class Contract:
    def __init__(self, client):
        self.client = client

    def contract_compile(self, code, options):
        """Compile a ring contract from source and return byte code"""
        data = self.client.local_http_post(
            'contract/compile',
            json={'code': code, 'options': options}
        )
        error = data.get('reason')
        if error:
            raise ContractError(error)
        return data

    def call(self, code, function, arg):
        '''"Call a ring function with a given name and argument in the given bytecode off chain.'''

        # see: /epoch/lib/aehttp-0.1.0/src/aehttp_dispatch_ext.erl
        data = self.client.local_http_post(
            'contract/call',
            json={
                'code': code,
                'function': function,
                'arg': arg
            }
        )
        error = data.get('reason')
        if error:
            raise ContractError(error)
        return data

    def encode_calldata(self, code, function, arg):
        data = self.client.local_http_post(
            'contract/encode-calldata',
            json={
                'code': code,
                'function': function,
                'arg': arg
            }
        )
        error = data.get('reason')
        if error:
            raise ContractError(error)
        return data['calldata']
