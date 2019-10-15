from aeternity import utils, defaults, hashing, openapi, identifiers, signing, compiler

import namedtupled


class ContractError(Exception):
    pass


class Contract:

    def __init__(self, **kwargs):
        """
        Initialize a contract object

        :param client: the node client to use
        """
        self.gas = kwargs.get('gas', defaults.CONTRACT_GAS)
        self.gas_price = kwargs.get('gas_price', defaults.CONTRACT_GAS_PRICE)
        self.fee = kwargs.get('fee', defaults.FEE)
        self.contract_amount = kwargs.get('amount', defaults.CONTRACT_AMOUNT)
        self.client = kwargs.get('client', None)
        self.account = kwargs.get('account', None)
        if not self.client:
            raise ValueError("Node client not provided")
        self.source = kwargs.get('source', None)
        address = kwargs.get('address', None)
        if address:
            self.at(address)
        self.bytecode = kwargs.get('bytecode', None)
        self.aci = kwargs.get('aci', None)
        self.compiler = kwargs.get('compiler', None)
        if self.account and type(self.account) is not signing.Account:
            raise TypeError("Invalid account type. Use `class Account` for creating an account")
        if self.compiler and isinstance(self.compiler, str):
            self.compiler = compiler.CompilerClient(self.compiler)
        if self.compiler and self.source:
            self.bytecode = self.compiler.compile(self.source)
            self.aci = self.compiler.aci(self.source)
        self.__generate_methods()

    def __generate_methods(self):
        if self.aci:
            for f in self.aci.encoded_aci.contract.functions:
                self.__add_contract_method(namedtupled.map({
                    "name": f.name,
                    "doc": f"Contract Method {f.name}",
                    "typeDef": f.arguments,
                    "stateful": f.stateful
                }, _nt_name="ContractMethod"))

    def __add_contract_method(self, method):
        def contract_method(*args, **kwargs):
            """ typeDef = method.typeDef
            isStateful = method.stateful """
        contract_method.__name__ = method.name
        contract_method.__doc__ = method.doc
        setattr(self, contract_method.__name__, contract_method)

    def call(self, contract_id,
             account, function, calldata,
             amount=defaults.CONTRACT_AMOUNT,
             gas=None,
             gas_price=None,
             fee=None,
             abi_version=None,
             tx_ttl=defaults.TX_TTL):
        """Call a sophia contract"""
        opts = self.__process_options(gas=gas, gas_price=gas_price, amount=amount, fee=fee, account=account)
        if self.address is None:
            raise ValueError("Contract Address not present. Use `at` method to set contract address.")
        # check if the contract exists
        try:
            self.client.get_contract(pubkey=self.address)
        except openapi.OpenAPIClientException:
            raise ContractError(f"Contract {self.address} not found")

        try:
            # retrieve the correct vm/abi version
            _, abi = self.client.get_vm_abi_versions()
            abi_version = abi if abi_version is None else abi_version
            # get the transaction builder
            txb = self.client.tx_builder
            # get the account nonce and ttl
            nonce, ttl = self.client._get_nonce_ttl(opts.account.get_address(), tx_ttl)
            # build the transaction
            tx = txb.tx_contract_call(account.get_address(), contract_id, calldata, function,
                                      amount, gas, gas_price, abi_version,
                                      fee, ttl, nonce)
            # sign the transaction
            tx_signed = self.client.sign_transaction(opts.account, tx)
            # post the transaction to the chain
            self.client.broadcast_transaction(tx_signed)
            return tx_signed
        except openapi.OpenAPIClientException as e:
            raise ContractError(e)

    def get_call_object(self, tx_hash):
        """
        retrieve the call object for a contract call transaction
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
            opts = self.__process_options(gas=gas, gas_price=gas_price, amount=amount, fee=fee, account=account)
            bytecode = bytecode if bytecode is not None else self.bytecode
            if bytecode is None:
                raise ValueError("bytecode not present. Either provide contract bytecode or set contract source using `setSource` method")
            # retrieve the correct vm/abi version
            vm, abi = self.client.get_vm_abi_versions()
            vm_version = vm if vm_version is None else vm_version
            abi_version = abi if abi_version is None else abi_version
            # get the transaction builder
            txb = self.client.tx_builder
            # get the account nonce and ttl
            nonce, ttl = self.client._get_nonce_ttl(opts.account.get_address(), tx_ttl)
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
