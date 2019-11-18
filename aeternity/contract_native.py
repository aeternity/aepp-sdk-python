from aeternity import utils, defaults, identifiers, signing, compiler
from aeternity.contract import Contract

import namedtupled


class ContractNative(object):

    def __init__(self, **kwargs):
        """
        Initialize a ContractNative object

        :param client: an instance of NodeClient
        :param source: the source code of the contract
        :param compiler: an instance of the CompilerClient
        :param address: address of the currently deployed contract (optional)
        :param gas: Gas to be used for all contract interactions (optional)
        :param fee: fee to be used for all contract interactions (optional)
        :param gas_price: Gas price to be used for all contract interactions (optional)
        :param account: Account to be used for contract deploy and contract calls (optional)
        :param use_dry_run: use dry run for all method calls except for payable and stateful methods (default: True)
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
        self.use_dry_run = kwargs.get('use_dry_run', True)

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
                    "arguments": f.arguments,
                    "returns": f.returns,
                    "stateful": f.stateful,
                    "payable": f.payable
                }, _nt_name="ContractMethod"))

    def __encode_method_args(self, method, *args):
        if len(args) != len(method.arguments):
            raise ValueError(f"Invalid number of arguments. Expected {len(method.arguments)}, Provided {len(args)}")
        transformed_args = []
        for i, val in enumerate(args):
            transformed_args.append(self.sophia_transformer.convert_to_sophia(val, namedtupled.reduce(method.arguments[i].type), self.aci.encoded_aci))
        return self.compiler.encode_calldata(self.source, method.name, *transformed_args).calldata

    def __decode_method_args(self, method, args):
        return self.sophia_transformer.convert_to_py(namedtupled.reduce(args), namedtupled.reduce(method.returns), self.aci.encoded_aci)

    def __add_contract_method(self, method):
        def contract_method(*args, **kwargs):
            calldata = self.__encode_method_args(method, *args)
            use_dry_run = kwargs.get('use_dry_run', self.use_dry_run)
            call_info = None
            if method.stateful or method.payable or not use_dry_run:
                tx_hash = self.call(method.name, calldata, **kwargs).hash
                call_info = namedtupled.reduce(self.contract.get_call_object(tx_hash))
                call_info['tx_hash'] = tx_hash
                call_info = namedtupled.map(call_info)
            else:
                call_info = self.call_static(method.name, calldata, **kwargs)
                if call_info.result == 'error':
                    raise ValueError(call_info.reason)
                call_info = call_info.call_obj
            decoded_call_result = self.compiler.decode_call_result(self.source, method.name, call_info.return_value, call_info.return_type)
            return call_info, self.__decode_method_args(method, decoded_call_result)
        contract_method.__name__ = method.name
        contract_method.__doc__ = method.doc
        setattr(self, contract_method.__name__, contract_method)

    def __process_options(self, **kwargs):
        gas = self.gas if kwargs.get('gas') is None else kwargs.get('gas')
        gas_price = self.gas_price if kwargs.get('gas_price') is None else kwargs.get('gas_price')
        amount = self.contract_amount if kwargs.get('amount') is None else kwargs.get('amount')
        fee = self.fee if kwargs.get('fee') is None else kwargs.get('fee')
        account = self.account if kwargs.get('account') is None else kwargs.get('account')
        if account is None:
            raise ValueError("Please provide an account to sign contract call transactions. You can set a default account using 'set_account' method")
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

    def set_account(self, account):
        if account is None:
            raise ValueError("Account can not be of None type")
        if type(account) is not signing.Account:
            raise TypeError("Invalid account type. Use `class Account` for creating an account")
        self.account = account

    def deploy(self, *arguments, entrypoint="init",
               deposit=defaults.CONTRACT_DEPOSIT,
               vm_version=None,
               abi_version=None,
               tx_ttl=defaults.TX_TTL,
               **kwargs):
        """
        Create a contract and deploy it to the chain
        :return: the transaction
        """
        method_list = list(filter(lambda f: f.name == entrypoint, self.aci.encoded_aci.contract.functions))
        calldata = None
        if len(method_list) == 1 and method_list[0].name == entrypoint:
            calldata = self.__encode_method_args(method_list[0], *arguments)
        else:
            calldata = self.compiler.encode_calldata(self.source, entrypoint, *arguments).calldata
        opts = self.__process_options(**kwargs)
        tx = self.contract.create(opts.account, self.bytecode, calldata, opts.amount, deposit, opts.gas,
                                  opts.gas_price, opts.fee, vm_version, abi_version, tx_ttl)
        self.at(tx.metadata.contract_id)
        return tx

    def call(self, function, calldata,
             abi_version=None,
             tx_ttl=defaults.TX_TTL,
             **kwargs):
        """
        call a contract method
        :return: the transaction
        """
        opts = self.__process_options(**kwargs)
        return self.contract.call(self.address, opts.account, function, calldata, opts.amount, opts.gas,
                                  opts.gas_price, opts.fee, abi_version, tx_ttl)

    def call_static(self, function, calldata,
                    abi_version=None,
                    tx_ttl=defaults.TX_TTL,
                    top=None,
                    **kwargs):
        """
        call-static a contract method
        :return: the call object
        """
        opts = self.__process_options(**kwargs)
        return self.contract.call_static(self.address, function, calldata, opts.account.get_address(), opts.amount, opts.gas,
                                         opts.gas_price, opts.fee, abi_version, tx_ttl, top)


class SophiaTransformation:

    TO_SOPHIA_METHOD_PREFIX = 'to_sophia_'
    FROM_SOPHIA_METHOD_PREFIX = 'from_sophia_'

    def __inject_vars(self, t, aci_types):
        [[base_type, generic]] = aci_types.items()
        [[_, variant_value]] = t.items()
        if base_type == 'variant':
            vars_map = []
            for x in generic:
                [tag, gen] = x.items()[0]
                gen_map = []
                for y in gen:
                    var_name_list = list(map(lambda e: e.name, aci_types['vars']))
                    if y in var_name_list:
                        index = var_name_list.index(y)
                        gen_map.append(variant_value[index])
                    else:
                        gen_map.append(y)
                vars_map.append({[tag]: gen_map})
            return {
                [base_type]: vars_map
            }

    def __link_type_def(self, t, bindings):
        _, type_defs = t.split('.') if isinstance(t, str) else list(t.keys())[0].split('.')
        aci_types = bindings.contract.type_defs + [namedtupled.map({"name": "state", "typedef": bindings.contract.state, "vars": []})]
        aci_types = filter(lambda x: x.name == type_defs, aci_types)
        aci_types = list(aci_types)[0]
        if len(list(aci_types.vars)) > 0:
            aci_types.typedef = self.__inject_vars(t, aci_types)
        return namedtupled.reduce(aci_types.typedef)

    def __extract_type(self, sophia_type, bindings={}):
        [t] = [sophia_type] if not isinstance(sophia_type, list) else sophia_type
        if len(bindings) > 0:
            if (isinstance(t, str) and bindings.contract.name in t) or (isinstance(t, dict) > 0 and bindings.contract.name in list(t.keys())[0]):
                t = self.__link_type_def(t, bindings)

        # map, tuple, list, record, bytes
        if isinstance(t, dict):
            [(key, val)] = t.items()
            return key, val
        # base types
        if isinstance(t, str):
            return t, None

    def convert_to_sophia(self, argument, sophia_type, bindings={}):
        current_type, generic = self.__extract_type(sophia_type, bindings)
        method_name = self.TO_SOPHIA_METHOD_PREFIX + current_type
        method = getattr(self, method_name, None)
        if method is None:
            return f'{argument}'
        return method(argument, generic, bindings)

    def convert_to_py(self, argument, sophia_type, bindings={}):
        current_type, generic = self.__extract_type(sophia_type, bindings)
        method_name = self.FROM_SOPHIA_METHOD_PREFIX + current_type
        method = getattr(self, method_name, None)
        if method is None:
            return argument
        return method(argument, generic, bindings)

    def to_sophia_string(self, arg, generic, bindings={}):
        return f'\"{arg}\"'

    def to_sophia_signature(self, arg, generic, bindings={}):
        return self.to_sophia_bytes(arg, generic, bindings={})

    def from_sophia_signature(self, arg, generic, bindings={}):
        return self.from_sophia_bytes(arg, generic, bindings={})

    def to_sophia_hash(self, arg, generic, bindings={}):
        return self.to_sophia_bytes(arg, generic, bindings={})

    def from_sophia_hash(self, arg, generic, bindings={}):
        return self.from_sophia_bytes(arg, generic, bindings={})

    def to_sophia_bytes(self, arg, generic, bindings={}):
        if isinstance(arg, str):
            return f'#{arg}'
        elif isinstance(arg, bytes):
            return f"{arg.hex()}"

    def from_sophia_bytes(self, arg, generic, bindings={}):
        return arg.split('#')[1]

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

    def from_sophia_map(self, arg, generic, bindings={}):
        [key_t, value_t] = generic
        result = {}
        for (key, val) in arg:
            key = self.convert_to_py(key, key_t, bindings)
            val = self.convert_to_py(val, value_t, bindings)
            result[key] = val
        return result

    def to_sophia_list(self, arg, generic, bindings={}):
        result = "["
        for val in arg:
            result += f"{self.convert_to_sophia(val, generic, bindings)},"
        return result[:-1] + "]"

    def from_sophia_list(self, arg, generic, bindings={}):
        result = []
        for x in arg:
            result.append(self.convert_to_py(x, generic, bindings))
        return result

    def to_sophia_option(self, arg, generic, bindings={}):
        return 'None' if arg is None else f"Some({self.convert_to_sophia(arg, generic, bindings)})"

    def from_sophia_option(self, arg, generic, bindings={}):
        if arg == 'None':
            return None
        else:
            [(variantType, [value])] = arg.items()
            if variantType == 'Some':
                return self.convert_to_py(value, generic, bindings)
            else:
                return None

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

    def from_sophia_record(self, arg, generic, bindings={}):
        result = {}
        generic_map = {}
        for val in generic:
            generic_map[val['name']] = {'type': val['type']}
        for [name, value] in arg.items():
            result[name] = self.convert_to_py(value, generic_map[name]['type'], bindings)
        return result

    def to_sophia_variant(self, arg, generic, bindings={}):
        [[variant, variant_args]] = [[arg, []]] if isinstance(arg, str) else arg.items()
        [[v, type_val]] = list(filter(lambda x: list(x.keys())[0].lower() == variant.lower(), generic))[0].items()
        transfrom_arg = ""
        if len(type_val) > 0:
            mapped_list = list(map(lambda i, x: self.convert_to_sophia(x, type_val[i], bindings), enumerate(variant_args[0:len(type_val)])))
            transfrom_arg = f"({mapped_list})"
        return f"{v}{transfrom_arg}"
