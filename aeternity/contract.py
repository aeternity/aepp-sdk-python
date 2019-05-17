from aeternity import exceptions
from aeternity import utils, defaults, hashing, openapi, identifiers
import requests
import namedtupled
from requests import ConnectionError


class CompilerError(exceptions.AException):
    """
    Throw when the compiler apis return an error
    """
    pass


class CompilerClient(object):
    """
    CompilerClient is the rest client to interact with the aesophia_http compiler
    """

    def __init__(self, compiler_url='http://localhost:3080'):
        self.compiler_url = compiler_url
        self.compiler_cli = openapi.OpenAPICli(compiler_url)

    def _post(self, path, body, _response_object_name="CompilerReply"):
        """
        Execute the post request to the compiler
        """
        http_reply = None
        try:
            http_reply = requests.post(f'{self.compiler_url}{path}', json=body)
            object_reply = namedtupled.map(http_reply.json(), _nt_name=_response_object_name)
            if http_reply.status_code == 200:
                return object_reply
            raise CompilerError(f"Error: {http_reply.desc}", code=http_reply.status_code)
        except ConnectionError as e:
            raise Exception(f"Connection error to the compiler at {self.compiler_url}", e)

    def compile(self, source_code, compiler_options={}):
        body = dict(
            code=source_code,
            options=compiler_options
        )
        return self.compiler_cli.compile_contract(body=body)

    def aci(self, source_code, compiler_options={}):
        body = dict(
            code=source_code,
            options=compiler_options
        )
        return self.compiler_cli.generate_aci(body=body)

    def encode_calldata(self, source_code, function_name, arguments=[]):
        if not isinstance(arguments, list):
            arguments = [arguments]
        if arguments is None:
            arguments = []
        body = dict(
            source=source_code,
            function=function_name,
            arguments=[str(v) for v in arguments]
        )
        return self.compiler_cli.encode_calldata(body=body)

    def decode_data(self, sophia_type, encoded_data):
        body = {
            "data": encoded_data,
            "sophia-type": sophia_type
        }
        return self.compiler_cli.decode_data(body=body)

    def decode_calldata_with_bytecode(self, bytecode, encoded_calldata):
        body = {
            "calldata": encoded_calldata,
            "bytecode": bytecode
        }
        return self.compiler_cli.decode_calldata_bytecode(body=body)

    def decode_calldata_with_sourcecode(self, sourcecode, function, encoded_calldata):
        body = {
            "source": sourcecode,
            "function": function,
            "calldata": encoded_calldata
        }
        return self.compiler_cli.decode_calldata_source(body=body)


class ContractError(Exception):
    pass


class Contract:
    EVM = 'evm'
    SOPHIA = 'sophia'

    def __init__(self, client):
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

    def call_static(self, contract_id):
        """
        Execute a static contract call
        """
        pass

    def call(self, contract_id,
             account, function, arg, calldata,
             amount=defaults.CONTRACT_AMOUNT,
             gas=defaults.CONTRACT_GAS,
             gas_price=defaults.CONTRACT_GAS_PRICE,
             fee=defaults.FEE,
             vm_version=None,
             abi_version=None,
             tx_ttl=defaults.TX_TTL):
        """Call a sophia contract"""

        if not utils.is_valid_hash(contract_id, prefix=identifiers.CONTRACT_ID):
            raise ValueError(f"Invalid contract id {contract_id}")
        # check if the contract exists
        try:
            self.client.get_contract(pubkey=contract_id)
        except exceptions.OpenAPIClientException:
            raise ContractError(f"Contract {contract_id} not found")

        try:
            # retrieve the correct vm/abi version
            vm, abi = self._get_vm_abi_versions()
            vm_version = vm if vm_version is None else vm_version
            abi_version = abi if abi_version is None else abi_version
            # get the transaction builder
            txb = self.client.tx_builder
            # get the account nonce and ttl
            nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
            # build the transaction
            tx = txb.tx_contract_call(account.get_address(), self.address, calldata, function, arg,
                                      amount, gas, gas_price, abi_version,
                                      fee, ttl, nonce)
            # sign the transaction
            tx_signed = self.client.sign_transaction(account, tx.tx)
            # post the transaction to the chain
            self.client.broadcast_transaction(tx_signed.tx, tx_signed.hash)
            return tx_signed
        except exceptions.OpenAPIClientException as e:
            raise ContractError(e)

    def get_call_object(self, tx_hash):
        """
        retrieve the call object for a contract call transactio
        """
        # unsigned transaction of the call
        call_object = self.client.get_transaction_info_by_hash(hash=tx_hash)
        # version 3.x.x
        if hasattr(call_object, "call_info"):
            return call_object.call_info
        # version 2.5.x
        return call_object

    def create(self,
               account,
               bytecode,
               amount=defaults.CONTRACT_AMOUNT,
               deposit=defaults.CONTRACT_DEPOSIT,
               init_calldata=defaults.CONTRACT_INIT_CALLDATA,
               gas=defaults.CONTRACT_GAS,
               gas_price=defaults.CONTRACT_GAS_PRICE,
               fee=defaults.FEE,
               vm_version=None,
               abi_version=None,
               tx_ttl=defaults.TX_TTL):
        """
        Create a contract and deploy it to the chain
        :return: the transaction
        """
        try:
            # retrieve the correct vm/abi version
            vm, abi = self._get_vm_abi_versions()
            vm_version = vm if vm_version is None else vm_version
            abi_version = abi if abi_version is None else abi_version
            # get the transaction builder
            txb = self.client.tx_builder
            # get the account nonce and ttl
            nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
            # build the transaction
            tx = txb.tx_contract_create(account.get_address(), bytecode, init_calldata,
                                        amount, deposit, gas, gas_price, vm_version, abi_version,
                                        fee, ttl, nonce)
            # store the contract address in the instance variabl
            self.address = hashing.contract_id(account.get_address(), nonce)
            # sign the transaction
            tx_signed = self.client.sign_transaction(account, tx, metadata={"contract_id": self.address})
            # post the transaction to the chain
            self.client.broadcast_transaction(tx_signed.tx, tx_signed.hash)
            return tx_signed
        except openapi.OpenAPIClientException as e:
            raise ContractError(e)

    def _get_vm_abi_versions(self):
        """
        Check the version of the node and retrieve the correct values for abi and vm version
        """
        protocol_version = self.client.get_consensus_protocol_version()
        if protocol_version == identifiers.PROTOCOL_ROMA:
            return identifiers.CONTRACT_ROMA_VM, identifiers.CONTRACT_ROMA_ABI
        if protocol_version == identifiers.PROTOCOL_MINERVA:
            return identifiers.CONTRACT_MINERVA_VM, identifiers.CONTRACT_MINERVA_ABI
        if protocol_version == identifiers.PROTOCOL_FORTUNA:
            return identifiers.CONTRACT_FORTUNA_VM, identifiers.CONTRACT_FORTUNA_ABI
        raise exceptions.UnsupportedNodeVersion(f"Version {self.client.api_version} is not supported")
