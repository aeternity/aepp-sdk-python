from aeternity import utils, defaults, identifiers, signing, compiler
from aeternity.contract import Contract

import namedtupled


class ContractNative(object):

    def __init__(self, **kwargs):
        """
        Initialize a ContractNative object

        :param source: the source code of the contract (optional)
        :param compiler: compiler url or instance of the CompilerClient
        :param bytecode: the bytecode of the contract (optional). If provided with the source and compiler, then the provided value will be overwritten.
        :param aci: the aci of the contract (optional). If provided with the source and compiler, then the provided value will be overwritten.
        :param address: address of the currently deployed contract (optional)
        :param gas: Gas to be used for all contract interactions (optional)
        :param fee: fee to be used for all contract interactions (optional)
        :param gas_price: Gas price to be used for all contract interactions (optional)
        :param account: Account to be used for contract deploy and contract calls (optional)
        """
        self.compiler = kwargs.get('compiler', None)
        if self.compiler is None:
            raise ValueError("Compiler is not provided")
        else:
            if isinstance(self.compiler, str):
                self.compiler = compiler.CompilerClient(self.compiler)
        self.source = kwargs.get('source', None)
        self.bytecode = kwargs.get('bytecode', None)
        self.aci = kwargs.get('aci', None)

        if self.aci is not None:
            self.aci = namedtupled.map(self.aci, _nt_name="ACI")
        if self.source is not None:
            self.bytecode = self.compiler.compile(self.source)
            self.aci = self.compiler.aci(self.source)
        if self.bytecode is None and self.aci is None:
            raise ValueError("Please provide either contract source or contract bytecode + aci")

        self.gas = kwargs.get('gas', defaults.CONTRACT_GAS)
        self.gas_price = kwargs.get('gas_price', defaults.CONTRACT_GAS_PRICE)
        self.fee = kwargs.get('fee', defaults.FEE)
        self.contract_amount = kwargs.get('amount', defaults.CONTRACT_AMOUNT)

        address = kwargs.get('address', None)
        if address:
            self.at(address)

        self.account = kwargs.get('account', None)
        if self.account and type(self.account) is not signing.Account:
            raise TypeError("Invalid account type. Use `class Account` for creating an account")

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
        self.deployed = True

    def deploy(self, init_calldata,
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
        opts = self.__process_options(gas=gas, gas_price=gas_price, amount=amount, fee=fee, account=account)
        _, contract_id = Contract.create(opts.account, self.bytecode, init_calldata, opts.amount, deposit, opts.gas,
                                         opts.gas_price, opts.fee, vm_version, abi_version, tx_ttl)
        self.at(contract_id)
        return contract_id


class SophiaTransformation:

    TO_SOPHIA_METHOD_PREFIX = 'to_sophia_'

    def convert_to_sophia(self, argument, sophia_type: str):
        method_name = self.TO_SOPHIA_METHOD_PREFIX + sophia_type
        method = getattr(self, method_name, None)
        if method is None:
            return f'{argument}'
        return method(argument)

    def to_sophia_string(self, arg):
        return f'/"{arg}/"'

    def to_sophia_signature(self, arg):
        return self.to_sophia_bytes(arg)

    def to_sophia_hash(self, arg):
        return self.to_sophia_bytes(arg)

    def to_sophia_bytes(self, arg):
        if isinstance(arg, str):
            return f'#{arg}'
        elif isinstance(arg, bytes):
            return f"{arg.hex()}"

    def to_sophia_bool(self, arg: bool):
        return "true" if arg else "false"

    def to_sophia_map(self, arg):
        pass

    def to_sophia_list(self, arg):
        pass

    def to_sophia_option(self, arg):
        pass

    def to_sophia_tuple(self, arg):
        pass

    def to_sophia_record(self, arg):
        pass

    def to_sophia_variant(self, arg):
        pass
