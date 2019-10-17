from aeternity import exceptions, __compiler_compatibility__
from aeternity import utils, defaults, hashing, openapi, identifiers

import namedtupled
import semver


class CompilerError(exceptions.AException):
    """
    Throw when the compiler apis return an error
    """
    pass


class CompilerClient(object):
    """
    The compiler client Fate version is the client for the aesophia_http compiler v4.x.x series,
    that is compatible with LIMA protocol (v4)
    """
    def __init__(self, compiler_url='http://localhost:3080', **kwargs):
        self.compiler_url = compiler_url
        self.compiler_cli = openapi.OpenAPICli(compiler_url, compatibility_version_range=__compiler_compatibility__)
        # chec the compatibiity node protocol
        self.target_protocol = identifiers.PROTOCOL_LIMA if semver.match(self.compiler_cli.version().version, ">3.9.9") else identifiers.PROTOCOL_FORTUNA
        self.compiler_options = {
        }
        if self.target_protocol >= identifiers.PROTOCOL_LIMA:
            self.set_option("backend", kwargs.get("backend", identifiers.COMPILER_OPTIONS_BACKEND_FATE))

    def set_option(self, name, value):
        self.compiler_options[name] = value

    def compile(self, source_code, compiler_options={}):
        compiler_options = compiler_options if len(compiler_options) > 0 else self.compiler_options
        body = dict(
            code=source_code,
            options=compiler_options
        )
        return self.compiler_cli.compile_contract(body=body)

    def aci(self, source_code, compiler_options={}):
        compiler_options = compiler_options if len(compiler_options) > 0 else self.compiler_options
        body = dict(
            code=source_code,
            options=compiler_options
        )
        return self.compiler_cli.generate_aci(body=body)

    def encode_calldata(self, contract_src, function_name, *arguments, compiler_options={}):
        """
        Encode calldata to be used to deploy or call a contract
        :param contract_src: the source code of the contract
        :param function_name: the name of the function to encode the calldata for
        :param arguments: the list of arguments of the funcition
        :compiler_options: to override the global compiler options
        """
        compiler_options = compiler_options if len(compiler_options) > 0 else self.compiler_options
        body = dict(
            source=contract_src,
            function=function_name,
            arguments=[str(v) for v in arguments],
            options=compiler_options
        )
        return self.compiler_cli.encode_calldata(body=body)

    def decode_data(self, sophia_type, encoded_data):
        body = {
            "data": encoded_data,
            "sophia-type": sophia_type
        }
        return self.compiler_cli.decode_data(body=body)

    def decode_call_result(self, sophia_type, encoded_data):
        body = {
            "data": encoded_data,
            "sophia-type": sophia_type
        }
        return self.compiler_cli.decode_data(body=body)

    def decode_calldata_with_bytecode(self, bytecode, encoded_calldata, compiler_options={}):
        compiler_options = compiler_options if len(compiler_options) > 0 else self.compiler_options
        body = {
            "calldata": encoded_calldata,
            "bytecode": bytecode,
            "backend": compiler_options.get("backend", self.compiler_options.get("backend", identifiers.COMPILER_OPTIONS_BACKEND_FATE))
        }
        return self.compiler_cli.decode_calldata_bytecode(body=body)

    def decode_calldata_with_sourcecode(self, sourcecode, function, encoded_calldata, compiler_options={}):
        compiler_options = compiler_options if len(compiler_options) > 0 else self.compiler_options
        body = {
            "source": sourcecode,
            "function": function,
            "calldata": encoded_calldata,
            "options": compiler_options
        }
        return self.compiler_cli.decode_calldata_source(body=body)

    @staticmethod
    def decode_bytecode(compiled):
        """
        Decode an encoded contract to it's components
        :param compiled: the encoded bytecode to decode as got from the 'compile' function
        :return: a named tuple with a decoded contract
        """
        if isinstance(compiled, str):
            if not utils.prefix_match(identifiers.BYTECODE, compiled):
                raise ValueError(f"Invalid input, expecting {identifiers.BYTECODE}_ prefix")
            # unpack the transaction
            raw_contract = hashing.decode_rlp(compiled)
        elif isinstance(compiled, bytes):
            # unpack the transaction
            raw_contract = hashing.decode_rlp(compiled)
        else:
            raise ValueError(f"Invalid input type")

        if not isinstance(raw_contract, list) or len(raw_contract) < 6:
            raise ValueError(f"Invalid contract structure")

        # print(raw_contract)
        tag = hashing._int_decode(raw_contract[0])
        vsn = hashing._int_decode(raw_contract[1])
        if tag != identifiers.OBJECT_TAG_SOPHIA_BYTE_CODE:
            raise ValueError(f"Invalid input, expecting object type {identifiers.OBJECT_TAG_SOPHIA_BYTE_CODE}, got {tag}")
        # this is the hash
        contract_data = dict(
            raw=raw_contract,
            tag=tag,
            vsn=vsn,
            src_hash=raw_contract[2],
            type_info=[],
            bytecode=raw_contract[4],
            compiler_version=hashing._binary_decode(raw_contract[5], str),
            # payable=raw_contract[6]
        )
        # print(type_info)
        for t in raw_contract[3]:
            contract_data["type_info"].append(dict(
                fun_hash=t[0],
                fun_name=hashing._binary_decode(t[1], str),
                arg_type=t[2],
                out_type=t[3],
            ))
        return namedtupled.map(contract_data, _nt_name="ContractBin")


class ContractError(Exception):
    pass


class Contract:

    def __init__(self, client):
        """
        Initialize a contract object

        :param client: the node client to use
        """
        self.client = client

    def call(self, contract_id,
             account, function, calldata,
             amount=defaults.CONTRACT_AMOUNT,
             gas=defaults.CONTRACT_GAS,
             gas_price=defaults.CONTRACT_GAS_PRICE,
             fee=defaults.FEE,
             abi_version=None,
             tx_ttl=defaults.TX_TTL):
        """Call a sophia contract"""

        if not utils.is_valid_hash(contract_id, prefix=identifiers.CONTRACT_ID):
            raise ValueError(f"Invalid contract id {contract_id}")
        # check if the contract exists
        try:
            self.client.get_contract(pubkey=contract_id)
        except openapi.OpenAPIClientException:
            raise ContractError(f"Contract {contract_id} not found")

        try:
            # retrieve the correct vm/abi version
            _, abi = self.client.get_vm_abi_versions()
            abi_version = abi if abi_version is None else abi_version
            # get the transaction builder
            txb = self.client.tx_builder
            # get the account nonce and ttl
            nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
            # build the transaction
            tx = txb.tx_contract_call(account.get_address(), contract_id, calldata, function,
                                      amount, gas, gas_price, abi_version,
                                      fee, ttl, nonce)
            # sign the transaction
            tx_signed = self.client.sign_transaction(account, tx)
            # post the transaction to the chain
            self.client.broadcast_transaction(tx_signed)
            return tx_signed
        except openapi.OpenAPIClientException as e:
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

    def create(self, account, bytecode, calldata,
               amount=defaults.CONTRACT_AMOUNT,
               deposit=defaults.CONTRACT_DEPOSIT,
               gas=defaults.CONTRACT_GAS,
               gas_price=defaults.CONTRACT_GAS_PRICE,
               fee=defaults.FEE,
               vm_version=None,
               abi_version=None,
               tx_ttl=defaults.TX_TTL):
        """
        Create a contract and deploy it to the chain
        :param account: the account signing the contract call and owner of the contract
        :param bytecode: the bytecode of the contract (ba_....)
        :param calldata: the calldata for the init function of the contract
        :param amount: TODO: define
        :param deposit: the deposit on the contract
        :param gas: the gas limit for the execution of the init funcion
        :param gas_price: the gas price for gas unit
        :param fee: the fee for the transaction
        :param vm_version: the virtual machine version
        :param abi_version: TODO
        :param tx_ttl: the transaction ttl
        :return: the transaction
        """
        try:
            # retrieve the correct vm/abi version
            vm, abi = self.client.get_vm_abi_versions()
            vm_version = vm if vm_version is None else vm_version
            abi_version = abi if abi_version is None else abi_version
            # get the transaction builder
            txb = self.client.tx_builder
            # get the account nonce and ttl
            nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
            # build the transaction
            tx = txb.tx_contract_create(account.get_address(), bytecode, calldata,
                                        amount, deposit, gas, gas_price, vm_version, abi_version,
                                        fee, ttl, nonce)
            # store the contract address in the instance variable
            contract_id = hashing.contract_id(account.get_address(), nonce)
            # sign the transaction
            tx_signed = self.client.sign_transaction(account, tx, metadata={"contract_id": contract_id})
            # post the transaction to the chain
            self.client.broadcast_transaction(tx_signed)
            return tx_signed
        except openapi.OpenAPIClientException as e:
            raise ContractError(e)
