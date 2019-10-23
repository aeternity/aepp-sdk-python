from aeternity import utils, defaults, identifiers, signing, compiler
from aeternity.contract import Contract

import namedtupled


class ContractNative(object):

    def __init__(self, **kwargs):
        """
        Initialize a ContractNative object

        :param client: instance of node client
        :param source: the source code of the contract (optional)
        :param compiler: compiler url or instance of the CompilerClient
        :param address: address of the currently deployed contract (optional)
        :param gas: Gas to be used for all contract interactions (optional)
        :param fee: fee to be used for all contract interactions (optional)
        :param gas_price: Gas price to be used for all contract interactions (optional)
        :param account: Account to be used for contract deploy and contract calls (optional)
        """
        if 'client' in kwargs:
            self.contract = Contract(kwargs.get('client'))
        else:
            raise ValueError("client is not provided")
        self.compiler = kwargs.get('compiler', None)
        if self.compiler is None:
            raise ValueError("Compiler is not provided")
        else:
            if isinstance(self.compiler, str):
                self.compiler = compiler.CompilerClient(self.compiler)
        self.source = kwargs.get('source', None)
        if self.source is not None:
            self.bytecode = self.compiler.compile(self.source).bytecode
            self.aci = self.compiler.aci(self.source)
        else:
            raise ValueError("contract source not provided")

        self.contract_name = self.aci.encoded_aci.contract.name
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
        self.sophia_transformer = SophiaTransformation()
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
            tansformed_args = []
            for i, val in enumerate(args):
                tansformed_args.append(self.sophia_transformer.convert_to_sophia(val, namedtupled.reduce(method.typeDef[i].type), self.aci.encoded_aci))
            calldata = self.compiler.encode_calldata(self.source, method.name, *tansformed_args).calldata
            call_tx = self.call(method.name, calldata)
            call_info = self.contract.get_call_object(call_tx.hash)
            return call_info
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

    def deploy(self, function, *arguments,
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
        calldata = self.compiler.encode_calldata(self.source, function, *arguments).calldata
        opts = self.__process_options(gas=gas, gas_price=gas_price, amount=amount, fee=fee, account=account)
        tx = self.contract.create(opts.account, self.bytecode, calldata, opts.amount, deposit, opts.gas,
                                  opts.gas_price, opts.fee, vm_version, abi_version, tx_ttl)
        self.at(tx.metadata.contract_id)
        return tx

    def call(self, function, calldata,
             account=None,
             amount=None,
             gas=None,
             gas_price=None,
             fee=None,
             abi_version=None,
             tx_ttl=defaults.TX_TTL):
        """
        call a contract method
        :return: the transaction
        """
        opts = self.__process_options(gas=gas, gas_price=gas_price, amount=amount, fee=fee, account=account)
        return self.contract.call(self.address, opts.account, function, calldata, opts.amount, opts.gas,
                                  opts.gas_price, opts.fee, abi_version, tx_ttl)


class SophiaTransformation:

    TO_SOPHIA_METHOD_PREFIX = 'to_sophia_'
    FROM_SOPHIA_METHOD_PREFIX = 'from_sophia_'

    def linkTypeDef(self, t, bindings):
        _, typeDef = t.split('.') if isinstance(t, str) else list(t.keys())[0].split('.')
        aciTypes = bindings.contract.type_defs + [namedtupled.map({"name": "state", "typedef": bindings.contract.state, "vars": []})]
        aciTypes = filter(lambda x: x.name == typeDef, aciTypes)
        # TODO: Inject vars
        return namedtupled.reduce(list(aciTypes)[0].typedef)

    def extractType(self, sophia_type, bindings={}):
        [t] = [sophia_type] if not isinstance(sophia_type, list) else sophia_type

        if len(bindings) > 0:
            if (isinstance(t, str) and bindings.contract.name in t) or (isinstance(t, dict) > 0 and bindings.contract.name in list(t.keys())[0]):
                t = self.linkTypeDef(t, bindings)

        # map, tuple, list, record, bytes
        if isinstance(t, dict):
            [(key, val)] = t.items()
            return key, val
        # base types
        if isinstance(t, str):
            return t, None

    def convert_to_sophia(self, argument, sophia_type, bindings={}):
        current_type, generic = self.extractType(sophia_type, bindings)
        method_name = self.TO_SOPHIA_METHOD_PREFIX + current_type
        method = getattr(self, method_name, None)
        if method is None:
            return f'{argument}'
        return method(argument, generic, bindings)

    def to_sophia_string(self, arg, generic, bindings={}):
        return f'\"{arg}\"'

    def to_sophia_signature(self, arg, generic, bindings={}):
        return self.to_sophia_bytes(arg)

    def to_sophia_hash(self, arg, generic, bindings={}):
        return self.to_sophia_bytes(arg)

    def to_sophia_bytes(self, arg, generic, bindings={}):
        if isinstance(arg, str):
            return f'#{arg}'
        elif isinstance(arg, bytes):
            return f"{arg.hex()}"

    def to_sophia_bool(self, arg, generic, bindings={}):
        return "true" if arg else "false"

    def to_sophia_map(self, arg, generic, bindings={}):
        if isinstance(arg, dict):
            arg = arg.items()
        result = '{'
        for i, val in enumerate(arg):
            k, v = val
            if i != 0:
                result += ','
            result += f"[{self.convert_to_sophia(k, generic[0], bindings)}] = {self.convert_to_sophia(v, generic[1], bindings)}"
        return result + '}'

    def to_sophia_list(self, arg, generic, bindings={}):
        result = "["
        for val in arg:
            result += f"{self.convert_to_sophia(val, generic, bindings)},"
        return result[:-1] + "]"

    def to_sophia_option(self, arg, generic, bindings={}):
        return 'None' if arg is None else f"Some({self.convert_to_sophia(arg, generic, bindings)})"

    def to_sophia_tuple(self, arg, generic, bindings={}):
        result = "("
        for i, val in enumerate(arg):
            result += f"{self.convert_to_sophia(val, generic[i], bindings)},"
        return result[:-1] + ")"

    def to_sophia_record(self, arg, generic, bindings={}):
        result = '{'
        for i, val in enumerate(generic):
            if i != 0:
                result += ','
            result += f"{val['name']} = {self.convert_to_sophia(arg[val['name']], val['type'], bindings)}"
        return result + '}'

    def to_sophia_variant(self, arg, generic, bindings={}):
        [[variant, variantArgs]] = [[arg, []]] if isinstance(arg, str) else arg.items()
        [[v, type_val]] = list(filter(lambda x: list(x.keys())[0].lower() == variant.lower(), generic))[0].items()
        transfrom_arg = ""
        if len(type_val) > 0:
            mapped_list = list(map(lambda i, x: self.convert_to_sophia(x, type_val[i], bindings), enumerate(variantArgs[0:len(type_val)])))
            transfrom_arg = f"({mapped_list})"
        return f"{v}{transfrom_arg}"
