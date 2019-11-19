from aeternity import utils, defaults, hashing, openapi, identifiers


class ContractError(Exception):
    pass


class Contract:

    def __init__(self, client):
        """
        Initialize a contract object
        :param client: the node client to use
        """
        self.client = client

    def __prepare_call_tx(self, contract_id, address, function, calldata,
                          amount, gas, gas_price, fee, abi_version, tx_ttl):
        """
        Prepare a Contract call transaction

        :param contract_id: the contract address
        :param address: the address preparing the transaction
        """

        if not utils.is_valid_hash(contract_id, prefix=identifiers.CONTRACT_ID):
            raise ValueError(f"Invalid contract id {contract_id}")
        # parse amounts
        amount, gas_price, fee = utils._amounts_to_aettos(amount, gas_price, fee)
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
            nonce, ttl = self.client._get_nonce_ttl(address, tx_ttl)
            # build the transaction
            return txb.tx_contract_call(address, contract_id, calldata, function,
                                        amount, gas, gas_price, abi_version, fee, ttl, nonce)
        except openapi.OpenAPIClientException as e:
            raise ContractError(e)

    def call_static(self, contract_id, function, calldata,
                    address=defaults.DRY_RUN_ADDRESS,
                    amount=defaults.DRY_RUN_AMOUNT,
                    gas=defaults.CONTRACT_GAS,
                    gas_price=defaults.CONTRACT_GAS_PRICE,
                    fee=defaults.FEE,
                    abi_version=None,
                    tx_ttl=defaults.TX_TTL,
                    top=None):
        """
        Call Static a sophia contract

        :param contract_id:TODO
        :param function: TODO
        :param calldata: TODO
        :param address: TODO
        :param amount: TODO
        :param gas: TODO
        :param gas_price: TODO
        :param fee: TODO
        :param abi_version:TODO
        :param tx_ttl: TODO
        :param top: TODO

        """

        try:
            tx = self.__prepare_call_tx(contract_id, address, function, calldata, amount, gas, gas_price, fee, abi_version, tx_ttl)
            account = {
                "amount": amount,
                "pub_key": address
            }
            body = {"txs": [{"tx": tx.tx}], "accounts": [account]}
            if top is not None and top.startswith('kh'):
                body['top'] = top
            result = self.client.dry_run_txs(body=body)
            return result.results[0]
        except openapi.OpenAPIClientException as e:
            raise ContractError(e)

    def call(self, contract_id,
             account, function, calldata,
             amount=defaults.CONTRACT_AMOUNT,
             gas=defaults.CONTRACT_GAS,
             gas_price=defaults.CONTRACT_GAS_PRICE,
             fee=defaults.FEE,
             abi_version=None,
             tx_ttl=defaults.TX_TTL):
        """Call a sophia contract"""

        try:
            tx = self.__prepare_call_tx(contract_id, account.get_address(), function, calldata, amount, gas, gas_price, fee, abi_version, tx_ttl)
            tx_signed = self.client.sign_transaction(account, tx)
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
        :param amount: amount to transfer to the account
        :param deposit: the deposit on the contract
        :param gas: the gas limit for the execution of the init function
        :param gas_price: the gas price for gas unit
        :param fee: the fee for the transaction
        :param vm_version: the virtual machine version
        :param abi_version: the abi version  to use
        :param tx_ttl: the transaction ttl
        :return: the transaction
        """
        try:
            # parse amounts
            deposit, amount, gas_price, fee = utils._amounts_to_aettos(deposit, amount, gas_price, fee)
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
