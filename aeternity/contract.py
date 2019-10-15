from aeternity import utils, defaults, hashing, openapi, identifiers, signing, compiler

import namedtupled


class ContractError(Exception):
    pass


class Contract(object):

    def __init__(self, **kwargs):
        """
        Initialize a contract object

        :param source: the source code of the contract (optional)
        :param address: address of the currently deployed contract (optional)
        :param bytecode: the bytecode of the contract (optional). If provided with the source and compiler, then the provided value will be overwritten.
        :param aci: the aci of the contract (optional). If provided with the source and compiler, then the provided value will be overwritten.
        :param compiler: compiler url or instance of the CompilerClient (optional)
        :param client: the aeternity client to use
        :param gas: Gas to be used for all contract interactions (optional)
        :param fee: fee to be used for all contract interactions (optional)
        :param gas_price: Gas price to be used for all contract interactions (optional)
        :param account: Account to be used for contract deploy and contract calls (optional)
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

    def __process_options(self, **kwargs):
        gas = self.gas if kwargs.get('gas') is None else kwargs.get('gas')
        gas_price = self.gas_price if kwargs.get('gas_price') is None else kwargs.get('gas_price')
        amount = self.contract_amount if kwargs.get('amount') is None else kwargs.get('amount')
        fee = self.fee if kwargs.get('fee') is None else kwargs.get('fee')
        account = self.account if kwargs.get('account') is None else kwargs.get('account')
        if account and type(account) is not signing.Account:
            raise TypeError("Invalid account type. Use `class Account` for creating an account")
        return namedtupled.map({
            "gas": gas,
            "gas_price": gas_price,
            "amount": amount,
            "fee": fee,
            "account": account
        }, _nt_name="ContractOptions")

    def at(self, address):
        """
        Set contract address
        """
        if not address or not utils.is_valid_hash(address, prefix=identifiers.CONTRACT_ID):
            raise ValueError(f"Invalid contract address {address}")
        self.address = address

    def setACI(self, aci):
        """
        Set contract ACI (if not provided during initialization)
        """
        if self.aci:
            raise ContractError("ACI is already present. ACI is only allowed to be set once.")
        if aci is None:
            raise ValueError("Invalid ACI")
        self.aci = aci
        self.__generate_methods()

    def setSource(self, source):
        """
        Set contract source (if not provided during initialization)
        """
        if self.source:
            raise ContractError("Source is already present. Source is only allowed to be set once.")
        if source is None:
            raise ValueError("Invalid contract source")
        self.source = source
        if self.compiler:
            self.bytecode = self.compiler.compile(self.source)
            if not self.aci:
                aci = self.compiler.aci(self.source)
                self.setACI(aci)

    def call_static(self, contract_id):
        """
        Execute a static contract call
        """
        pass

    def call(self,
             function, args, calldata,
             account=None,
             amount=None,
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
            tx = txb.tx_contract_call(opts.account.get_address(), self.address, calldata, function, args,
                                      opts.amount, opts.gas, opts.gas_price, abi_version,
                                      opts.fee, ttl, nonce)
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

    def create(self,
               init_calldata,
               bytecode=None,
               account=None,
               amount=None,
               deposit=defaults.CONTRACT_DEPOSIT,
               gas=None,
               gas_price=None,
               fee=None,
               vm_version=None,
               abi_version=None,
               tx_ttl=defaults.TX_TTL):
        """
        Create a contract and deploy it to the chain
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
            tx = txb.tx_contract_create(opts.account.get_address(), bytecode, init_calldata,
                                        opts.amount, deposit, opts.gas, opts.gas_price, vm_version, abi_version,
                                        opts.fee, ttl, nonce)
            # store the contract address in the instance variable
            self.address = hashing.contract_id(opts.account.get_address(), nonce)
            # sign the transaction
            tx_signed = self.client.sign_transaction(opts.account, tx, metadata={"contract_id": self.address})
            # post the transaction to the chain
            self.client.broadcast_transaction(tx_signed)
            return tx_signed
        except openapi.OpenAPIClientException as e:
            raise ContractError(e)
