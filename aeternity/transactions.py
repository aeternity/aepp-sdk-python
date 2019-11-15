from aeternity.hashing import _int, _int_decode, _binary, _binary_decode, _id, _id_decode, encode, decode, hash_encode
from aeternity.openapi import OpenAPICli
from aeternity import identifiers as idf
from aeternity import defaults

import rlp
import math
import pprint
import namedtupled
import copy


_INT = 0  # int type
_ID = 1  # id type (account, contract_id, etc)
_TX = 2  # transaction type
_SG = 3  # signatures
_PTR = 6  # name pointer
_POI = 7  # proof of inclusion
_OTTL_TYPE = 8  # oracle ttl
_BIN = 9  # binary format
_TR = 10  # tree
_VM_ABI = 11  # vm + abi field
_ENC = 12  # encoded object
_IDS = 101  # list of id
_PTRS = 106  # list of pointers


SIZE_BASED = 0  # used for most of transactions
TTL_BASED = 1  # used for oracle
GA_META = 2  # used for meta tx


class Fd:
    """
    Fd, shorthand for FieldDefinition, is a support class to
    """
    def __init__(self, index, field_type=_INT, **kwargs):
        self.index = index
        self.field_type = field_type
        self.encoding_prefix = kwargs.get("prefix")
        self.data_type = kwargs.get("data_type", bytes)

    def __str__(self):
        return f"{self.index}:{self.field_type}"

    def __repr__(self):
        return self.__str__()


class Fee:
    def __init__(self, fee_type, base_gas_multiplier=1, ttl_field=None, tx_field=None):
        self.fee_type = fee_type
        self.base_gas_multiplier = base_gas_multiplier
        self.ttl_field = ttl_field
        self.tx_field = tx_field

    def __str__(self):
        return f"ttl_type:{self.fee_type},mult:{self.base_gas_multiplier}"

    def __repr__(self):
        return self.__str__()


tx_descriptors = {
    (idf.OBJECT_TAG_SIGNED_TRANSACTION, 1): {
        "fee": None,  # signed transactions do not have fees
        "schema": {
            "version": Fd(1),
            "signatures": Fd(2, _SG, prefix=idf.SIGNATURE),  # list
            "tx": Fd(3, _TX, prefix=idf.TRANSACTION),
        }
    },
    (idf.OBJECT_TAG_SPEND_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "sender_id": Fd(2, _ID),
            "recipient_id": Fd(3, _ID),
            "amount": Fd(4),
            "fee": Fd(5),
            "ttl": Fd(6),
            "nonce": Fd(7),
            "payload": Fd(8, _ENC, prefix=idf.BYTE_ARRAY),
        }
    },
    (idf.OBJECT_TAG_NAME_SERVICE_PRECLAIM_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "account_id": Fd(2, _ID),
            "nonce": Fd(3),
            "commitment_id": Fd(4, _ID),
            "fee": Fd(5),
            "ttl": Fd(6),
        }},
    (idf.OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "account_id": Fd(2, _ID),
            "nonce": Fd(3),
            "name": Fd(4, _BIN, data_type=str),
            "name_salt": Fd(5),
            "fee": Fd(6),
            "ttl": Fd(7),
        }},
    (idf.OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION, 2): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "account_id": Fd(2, _ID),
            "nonce": Fd(3),
            "name": Fd(4, _BIN, data_type=str),
            "name_salt": Fd(5),
            "name_fee": Fd(6),
            "fee": Fd(7),
            "ttl": Fd(8),
        }},
    (idf.OBJECT_TAG_NAME_SERVICE_UPDATE_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "account_id": Fd(2, _ID),
            "nonce": Fd(3),
            "name_id": Fd(4, _ID),
            "name_ttl": Fd(5),
            "pointers": Fd(6, _PTR),
            "client_ttl": Fd(7),
            "fee": Fd(8),
            "ttl": Fd(9),
        }},
    (idf.OBJECT_TAG_NAME_SERVICE_TRANSFER_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "account_id": Fd(2, _ID),
            "nonce": Fd(3),
            "name_id": Fd(4, _ID),
            "recipient_id": Fd(5, _ID),
            "fee": Fd(6),
            "ttl": Fd(7),
        }},
    (idf.OBJECT_TAG_NAME_SERVICE_REVOKE_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "account_id": Fd(2, _ID),
            "nonce": Fd(3),
            "name_id": Fd(4, _ID),
            "fee": Fd(5),
            "ttl": Fd(6),
        }},
    (idf.OBJECT_TAG_CONTRACT_CREATE_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED, base_gas_multiplier=5),
        "schema": {
            "version": Fd(1),
            "owner_id": Fd(2, _ID),
            "nonce": Fd(3),
            "code": Fd(4, _ENC, prefix=idf.BYTECODE),
            # "vm_version": Fd(5),
            "abi_version": Fd(5, _VM_ABI),
            "fee": Fd(6),
            "ttl": Fd(7),
            "deposit": Fd(8),
            "amount": Fd(9),
            "gas": Fd(10),
            "gas_price": Fd(11),
            "call_data": Fd(12, _ENC, prefix=idf.BYTECODE),
        }},
    (idf.OBJECT_TAG_CONTRACT_CALL_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED, base_gas_multiplier=30),
        "schema": {
            "version": Fd(1),
            "caller_id": Fd(2, _ID),
            "nonce": Fd(3),
            "contract_id": Fd(4, _ID),
            "abi_version": Fd(5),
            "fee": Fd(6),
            "ttl": Fd(7),
            "amount": Fd(8),
            "gas": Fd(9),
            "gas_price": Fd(10),
            "call_data": Fd(11, _ENC, prefix=idf.BYTECODE),
        }},
    (idf.OBJECT_TAG_CHANNEL_CREATE_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "initiator": Fd(2, _ID),
            "initiator_amount": Fd(3),
            "responder": Fd(4, _ID),
            "responder_amount": Fd(5),
            "channel_reserve": Fd(6),
            "lock_period": Fd(7),
            "ttl": Fd(8),
            "fee": Fd(9),
            "delegate_ids": Fd(10, _IDS),  # [d(d) for d in tx_native[10]], TODO: are u sure
            "state_hash": Fd(11, _ENC, prefix=idf.STATE_HASH),
            "nonce": Fd(12),
        }},
    (idf.OBJECT_TAG_CHANNEL_DEPOSIT_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "channel_id": Fd(2, _ID),
            "from_id": Fd(3, _ID),
            "amount": Fd(4),
            "ttl": Fd(5),
            "fee": Fd(6),
            "state_hash": Fd(7, _ENC, prefix=idf.STATE_HASH),  # _binary_decode(tx_native[7]),
            "round": Fd(8),
            "nonce": Fd(9),
        }},
    (idf.OBJECT_TAG_CHANNEL_WITHDRAW_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "channel_id": Fd(2, _ID),
            "to_id": Fd(3, _ID),
            "amount": Fd(4),
            "ttl": Fd(5),
            "fee": Fd(6),
            "state_hash": Fd(7, _ENC, prefix=idf.STATE_HASH),  # _binary_decode(tx_native[7]),
            "round": Fd(8),
            "nonce": Fd(9),
        }},
    (idf.OBJECT_TAG_CHANNEL_CLOSE_MUTUAL_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "channel_id": Fd(2, _ID),
            "from_id": Fd(3, _ID),
            "initiator_amount_final": Fd(4),
            "responder_amount_final": Fd(5),
            "ttl": Fd(6),
            "fee": Fd(7),
            "nonce": Fd(8),
        }},
    (idf.OBJECT_TAG_CHANNEL_CLOSE_SOLO_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "channel_id": Fd(2, _ID),
            "from_id": Fd(3, _ID),
            "payload": Fd(4, _ENC, prefix=idf.BYTE_ARRAY),
            "poi": Fd(5, _POI),
            "ttl": Fd(6),
            "fee": Fd(7),
            "nonce": Fd(8),
        }},
    (idf.OBJECT_TAG_CHANNEL_SLASH_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "channel_id": Fd(2, _ID),
            "from_id": Fd(3, _ID),
            "payload": Fd(4, _ENC, prefix=idf.BYTE_ARRAY),
            "poi": Fd(5, _POI),
            "ttl": Fd(6),
            "fee": Fd(7),
            "nonce": Fd(8),
        }},
    (idf.OBJECT_TAG_CHANNEL_SETTLE_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "channel_id": Fd(2, _ID),
            "from_id": Fd(3, _ID),
            "initiator_amount_final": Fd(4),
            "responder_amount_final": Fd(5),
            "ttl": Fd(6),
            "fee": Fd(7),
            "nonce": Fd(8),
        }},
    (idf.OBJECT_TAG_CHANNEL_SNAPSHOT_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "channel_id": Fd(2, _ID),
            "from_id": Fd(3, _ID),
            "payload": Fd(4, _ENC, prefix=idf.BYTE_ARRAY),
            "ttl": Fd(5),
            "fee": Fd(6),
            "nonce": Fd(7),
        }},
    (idf.OBJECT_TAG_CHANNEL_FORCE_PROGRESS_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fd(1),
            "channel_id": Fd(2, _ID),
            "from_id": Fd(3, _ID),
            "payload": Fd(4, _ENC, prefix=idf.BYTE_ARRAY),
            "round": Fd(5),
            "update": Fd(6),  # _binary_decode(tx_native[2]),
            "state_hash": Fd(7, _ENC, prefix=idf.STATE_HASH),  # _binary_decode(tx_native[2]),
            "offchain_trees": Fd(8, _TR),  # TODO: implement support for _trees
            "ttl": Fd(2),
            "fee": Fd(2),
            "nonce": Fd(2),
        }},
    (idf.OBJECT_TAG_ORACLE_REGISTER_TRANSACTION, 1): {
        "fee": Fee(TTL_BASED, ttl_field="oracle_ttl_value"),
        "schema": {
            "version": Fd(1),
            "account_id": Fd(2, _ID),
            "nonce": Fd(3),
            "query_format": Fd(4, _BIN),  # _binary_decode(tx_native[4]), TODO: verify the type
            "response_format": Fd(5, _BIN),  # _binary_decode(tx_native[5]),
            "query_fee": Fd(6),
            "oracle_ttl_type": Fd(7, _OTTL_TYPE),
            "oracle_ttl_value": Fd(8),
            "fee": Fd(9),
            "ttl": Fd(10),
            "vm_version": Fd(11),
        }},
    (idf.OBJECT_TAG_ORACLE_QUERY_TRANSACTION, 1): {
        "fee": Fee(TTL_BASED, ttl_field="query_ttl_value"),
        "schema": {
            "version": Fd(1),
            "sender_id": Fd(2, _ID),
            "nonce": Fd(3),
            "oracle_id": Fd(4, _ID),
            "query": Fd(5, _BIN),
            "query_fee": Fd(6),
            "query_ttl_type": Fd(7, _OTTL_TYPE),
            "query_ttl_value": Fd(8),
            "response_ttl_type": Fd(9, _OTTL_TYPE),
            "response_ttl_value": Fd(10),
            "fee": Fd(11),
            "ttl": Fd(12),
        }},
    (idf.OBJECT_TAG_ORACLE_RESPONSE_TRANSACTION, 1): {
        "fee": Fee(TTL_BASED, ttl_field="response_ttl_value"),
        "schema": {
            "version": Fd(1),
            "oracle_id": Fd(2, _ID),
            "nonce": Fd(3),
            "query_id": Fd(4, _ENC, prefix=idf.ORACLE_QUERY_ID),
            "response": Fd(5, _BIN),
            "response_ttl_type": Fd(6, _OTTL_TYPE),
            "response_ttl_value": Fd(7),
            "fee": Fd(8),
            "ttl": Fd(9),
        }},
    (idf.OBJECT_TAG_ORACLE_EXTEND_TRANSACTION, 1): {
        "fee": Fee(TTL_BASED, ttl_field="oracle_ttl_value"),
        "schema": {
            "version": Fd(1),
            "oracle_id": Fd(2, _ID),
            "nonce": Fd(3),
            "oracle_ttl_type": Fd(4, _OTTL_TYPE),
            "oracle_ttl_value": Fd(5),
            "fee": Fd(6),
            "ttl": Fd(7),
        }},
    (idf.OBJECT_TAG_GA_ATTACH_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED, base_gas_multiplier=5),
        "schema": {
            "version": Fd(1),
            "owner_id": Fd(2, _ID),
            "nonce": Fd(3),
            "code": Fd(4, _ENC, prefix=idf.BYTECODE),
            "auth_fun": Fd(5, _BIN),
            # "vm_version": Fd(6), # This field is retrieved via abi_version
            "abi_version": Fd(6, _VM_ABI),
            "fee": Fd(7),
            "ttl": Fd(8),
            "gas": Fd(9),
            "gas_price": Fd(10),
            "call_data": Fd(11, _ENC, prefix=idf.BYTECODE),  # _binary_decode(tx_native[11]),
        }},
    (idf.OBJECT_TAG_GA_META_TRANSACTION, 1): {
        "fee": Fee(SIZE_BASED, base_gas_multiplier=5),
        "schema": {
            "version": Fd(1),
            "ga_id": Fd(2, _ID),
            "auth_data": Fd(3, _ENC, prefix=idf.BYTECODE),
            "abi_version": Fd(4),
            "fee": Fd(5),
            "gas": Fd(6),
            "gas_price": Fd(7),
            "ttl": Fd(8),
            "tx": Fd(9, _TX),
        }
    },
}


class TxObject:
    """
    This is a TxObject that is used throughout the SDK for transactions
    It contains all the info associated to a transaction like transaction data,transaction hash, etx

    """

    def __init__(self, **kwargs):
        self.set_data(kwargs.get("data", None))
        self.tx = kwargs.get("tx", None)
        self.hash = kwargs.get("hash", None)
        self.set_metadata(kwargs.get("metadata", None))

    def set_data(self, data):
        self.data = namedtupled.map(data, _nt_name="TxData")

    def set_metadata(self, metadata):
        self.metadata = namedtupled.map(metadata, _nt_name="TxMeta")

    def asdict(self):
        t = dict(
            data=namedtupled.reduce(self.data),
            metadata=namedtupled.reduce(self.metadata),
            tx=self.tx,
        )
        if self.hash is not None:
            t["hash"] = self.hash
        if "tx" in t.get("data", {}):
            t["data"]["tx"] = t["data"]["tx"].asdict()

        return t

    def get_signatures(self):
        """
        retrieves the list of signatures for a signed transaction, otherwise returns a empty list
        """
        if self.data.tag == idf.OBJECT_TAG_SIGNED_TRANSACTION:
            return self.data.signatures
        return []

    def get_signature(self, index):
        """
        get the signature at the requested index, or raise type error if there is no such index
        """
        sgs = self.get_signatures()
        if index < 0 or index >= len(sgs):
            raise TypeError(f"there is no signature at index {index}")
        return sgs[index]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return pprint.pformat(self.data)


class TxSigner:
    """
    TxSigner is used to sign transactions
    """

    def __init__(self, account, network_id):
        if account is None:
            raise ValueError("Account must be set to sign transactions")
        if network_id is None:
            raise ValueError("Network ID must be set to sign transactions")
        self.account = account
        self.network_id = network_id

    def sign_transaction(self, transaction: TxObject, metadata: dict = None) -> str:
        """
        Sign, encode and compute the hash of a transaction
        :param tx: the TxObject to be signed
        :param metadata: additional data to include in the output of the signed transaction object
        :return: encoded_signed_tx, encoded_signature, tx_hash
        """
        # get the transaction as byte list
        tx_raw = decode(transaction.tx)
        # sign the transaction
        signature = self.account.sign(_binary(self.network_id) + tx_raw)
        # pack and encode the transaction
        return encode(idf.SIGNATURE, signature)


class TxBuilder:
    """
    TxBuilder is used to build and post transactions to the chain.
    """

    def __init__(self,
                 base_gas=defaults.BASE_GAS,
                 gas_per_byte=defaults.GAS_PER_BYTE,
                 gas_price=defaults.GAS_PRICE,
                 key_block_interval=defaults.KEY_BLOCK_INTERVAL):
        self.base_gas = base_gas
        self.gas_per_byte = gas_per_byte
        self.gas_price = gas_price
        self.key_block_interval = key_block_interval

    @staticmethod
    def compute_tx_hash(encoded_tx: str) -> str:
        """
        Generate the hash from a signed and encoded transaction
        :param encoded_tx: an encoded signed transaction
        """
        tx_raw = decode(encoded_tx)
        return hash_encode(idf.TRANSACTION_HASH, tx_raw)

    def compute_min_fee(self, tx_data: dict, tx_descriptor: dict, tx_raw: list) -> int:
        # if the fee is none means it is not necessary to compute the fee
        if tx_descriptor.get("fee") is None:
            return 0
        # extract the parameters from the descriptor
        fee_field_index = tx_descriptor.get("schema").get("fee").index
        base_gas_multiplier = tx_descriptor.get("fee").base_gas_multiplier
        fee_type = tx_descriptor.get("fee").fee_type
        # if the fee is ttl based compute the ttl component
        ttl_component = 0
        if fee_type is TTL_BASED:
            ttl = tx_data.get(tx_descriptor.get("fee").ttl_field)
            ttl_component += (math.ceil(32000 * ttl / math.floor(60 * 24 * 365 / self.key_block_interval)))
        # if the fee is for a ga meta compute the enclosed tx size based fee
        ga_surplus = 0
        if fee_type == GA_META:
            tx_size = len(tx_raw[tx_descriptor.get("tx").index])
            ga_surplus = (self.base_gas * base_gas_multiplier + tx_size * self.gas_per_byte)
        # begin calculation
        current_fee, min_fee = -1, defaults.FEE
        while current_fee != min_fee:
            # save the min fee into current fee
            current_fee = min_fee
            # update the fee value
            tx_raw[fee_field_index] = _int(current_fee)
            # first calculate the size part
            tx_size = len(rlp.encode(tx_raw))
            min_fee = self.base_gas * base_gas_multiplier + tx_size * self.gas_per_byte
            # add the ttl_component
            min_fee += ttl_component
            # remove the ga_surplus
            min_fee -= ga_surplus
            # finally multiply for gas the gas price
            min_fee *= self.gas_price

        return min_fee

    def _jsontx_to_txobject(self, api_data):
        """
        Transform a dictionary built from a json reply  from the node to a transaction object.
        a the input api_data must be obtained from a /transactions/tx_xyz endpoint.

        A specific case is the one for signed transactions that in the api are treated in
        a different ways from other transactions, and their data is mixed with block informations
        """
        # transform the data to a dict since the openapi module maps them to a named tuple
        tx_data = namedtupled.reduce(api_data)
        if "signatures" in tx_data:
            tx_data["tag"] = idf.OBJECT_TAG_SIGNED_TRANSACTION
            tx_data["type"] = idf.TRANSACTION_TAG_TO_TYPE.get(idf.OBJECT_TAG_SIGNED_TRANSACTION)
            tx_data["version"] = 1
            # signed tx, extract the inner tx
            tx_data["tx"] = self._jsontx_to_txobject(api_data.tx)
        tx_data["tag"] = idf.TRANSACTION_TYPE_TO_TAG.get(tx_data.get("type"))
        # encode th tx in rlp
        tag = tx_data.get("tag")
        vsn = tx_data.get("version")
        # check if we have something
        descriptor = tx_descriptors.get((tag, vsn))
        if descriptor is None:
            # the transaction is not defined
            raise TypeError(f"Unknown transaction tag/version: {tag}/{vsn}")

        # flatten the oracle_ttl fields
        def flatten_ttl(key, data):
            ttl = data.pop(key)
            data[f"{key}_type"] = ttl.get("type")
            data[f"{key}_value"] = ttl.get("value")

        if tag == idf.OBJECT_TAG_ORACLE_QUERY_TRANSACTION:
            flatten_ttl("query_ttl", tx_data)
            flatten_ttl("response_ttl", tx_data)
        if tag in [idf.OBJECT_TAG_ORACLE_REGISTER_TRANSACTION, idf.OBJECT_TAG_ORACLE_EXTEND_TRANSACTION]:
            flatten_ttl("oracle_ttl", tx_data)
        if tag == idf.OBJECT_TAG_ORACLE_RESPONSE_TRANSACTION:
            flatten_ttl("response_ttl", tx_data)

        # do not compute the fee for a signed transaction
        compute_hash = True if tag == idf.OBJECT_TAG_SIGNED_TRANSACTION else False
        return self._txdata_to_txobject(tx_data, descriptor, compute_hash=compute_hash)

    def _txdata_to_txobject(self, data: dict, descriptor: dict, metadata: dict = {}, compute_hash=True) -> TxObject:
        # initialize the right data size
        # this is PYTHON to POSTBODY
        schema = descriptor.get("schema", [])
        raw_data = [0] * (len(schema) + 1)  # the +1 is for the tag
        # set the tx tag first
        raw_data[0] = _int(data.get("tag"))
        # parse fields and encode them
        for label, fn in schema.items():
            if fn.field_type == _INT:
                raw_data[fn.index] = _int(data.get(label, 0))
            elif fn.field_type == _ID:
                raw_data[fn.index] = _id(data.get(label))
            elif fn.field_type == _ENC:
                raw_data[fn.index] = decode(data.get(label))
            elif fn.field_type == _OTTL_TYPE:
                raw_data[fn.index] = _int(idf.ORACLE_TTL_TYPES.get(data.get(label)))
            elif fn.field_type == _SG:
                # signatures are always a list
                raw_data[fn.index] = [decode(sg) for sg in data.get(label, [])]
            elif fn.field_type == _VM_ABI:
                # vm/abi are encoded in the same 32bit length block
                raw_data[fn.index] = _int(data.get("vm_version")) + _int(data.get("abi_version"), 2)
            elif fn.field_type == _BIN:
                # this are binary string #TODO: may be byte array
                raw_data[fn.index] = _binary(data.get(label))
            elif fn.field_type == _PTR:
                # this are name pointers
                raw_data[fn.index] = [[_binary(p.get("key")), _id(p.get("id"))] for p in data.get(label, [])]
            elif fn.field_type == _TX:
                # this can be raw or tx object
                tx = data.get(label).tx if hasattr(data.get(label), "tx") else data.get(label)
                raw_data[fn.index] = decode(tx)
        # encode the transaction in rlp
        rlp_tx = rlp.encode(raw_data)
        # encode the tx in base64
        rlp_b64_tx = encode(idf.TRANSACTION, rlp_tx)
        # copy the data before modifying
        tx_data = copy.deepcopy(data)
        # build the tx object
        txo = TxObject(
            data=namedtupled.map(tx_data, _nt_name="TxData"),
            tx=rlp_b64_tx,
        )
        # compute the tx hash
        if compute_hash:
            txo.hash = hash_encode(idf.TRANSACTION_HASH, rlp_tx)
        # copy the metadata if exists or initialize it if None
        tx_meta = copy.deepcopy(metadata) if metadata is not None else {}
        # compute the minimum fee
        if descriptor.get("fee") is not None:
            tx_meta["min_fee"] = self.compute_min_fee(data, descriptor, raw_data)
        # only set the metadata if it is not empty
        txo.set_metadata(tx_meta)
        return txo

    def _rlptx_to_txobject(self, rlp_data: bytes) -> TxObject:
        """
        Transform an rlp encoded byte array transaction to a transaction object
        """
        # decode the rlp
        raw = rlp.decode(rlp_data)
        tag = _int_decode(raw[0])
        vsn = _int_decode(raw[1])
        # TODO: verify that the schema is there
        descriptor = tx_descriptors.get((tag, vsn))
        if descriptor is None:
            # the transaction is not defined
            raise TypeError(f"Unknown transaction tag/version: {tag}/{vsn}")
        schema = descriptor.get("schema")
        tx_data = {"tag": tag, "type": idf.TRANSACTION_TAG_TO_TYPE.get(tag)}
        for label, fn in schema.items():
            if fn.field_type == _INT:
                tx_data[label] = _int_decode(raw[fn.index])
            if fn.field_type == _ID:
                tx_data[label] = _id_decode(raw[fn.index])
            elif fn.field_type == _ENC:
                tx_data[label] = encode(fn.encoding_prefix, raw[fn.index])
            elif fn.field_type == _OTTL_TYPE:
                ttl_type = _int_decode(raw[fn.index])
                tx_data[fn.index] = idf.ORACLE_TTL_TYPES_REV.get(ttl_type)
            elif fn.field_type == _SG:
                # signatures are always a list
                tx_data[label] = [encode(idf.SIGNATURE, sg) for sg in raw[fn.index]]
            elif fn.field_type == _VM_ABI:
                vml = len(raw[fn.index])
                # vm/abi are encoded in the same 32bit length block
                tx_data["vm_version"] = _int_decode(raw[fn.index][0:vml - 2])
                tx_data["abi_version"] = _int_decode(raw[fn.index][vml - 2:])
            elif fn.field_type == _BIN:
                # this are byte arrays
                tx_data[label] = _binary_decode(raw[fn.index], data_type=fn.data_type)
            elif fn.field_type == _PTR:
                # this are name pointers
                tx_data[label] = [{"key": _binary_decode(p[0], data_type=str), "id": _id_decode(p[1])} for p in raw[fn.index]]
            elif fn.field_type == _TX:
                # this can be raw or tx object
                tx_data[label] = self._rlptx_to_txobject(raw[fn.index])
        # re-encode the decode object
        compute_hash = True if tag == idf.OBJECT_TAG_SIGNED_TRANSACTION else False
        return self._txdata_to_txobject(tx_data, descriptor, compute_hash=compute_hash)

    def _build_txobject(self, tx_data, metadata={}) -> TxObject:
        """
        function used internally to the TxBuilder to build the transaction
        and set the defaults when required
        """
        # 1. (namedtuple) from api queries so everything is wrapped around a json object that is a  generic signed transaction
        # 2. (string) from and b64c encoded rlp tx
        # 3. (dict) from functions of this class
        tag = tx_data.get("tag")
        vsn = tx_data.get("version")
        # check if we have something
        descriptor = tx_descriptors.get((tag, vsn))
        if descriptor is None:
            # the transaction is not defined
            raise TypeError(f"Unknown transaction tag/version: {tag}/{vsn}")
        # build the tx object
        txo = self._txdata_to_txobject(tx_data, descriptor, metadata=metadata)
        # check whenever we need to automatically assign the fee
        # we use -1 as default since for the signed tx there is no field fee
        if tx_data.get("fee", -1) == 0:
            tx_data["fee"] = txo.metadata.min_fee
            txo = self._txdata_to_txobject(tx_data, descriptor, metadata)
        return txo

    def parse_node_reply(self, tx_data) -> TxObject:
        """
        Parse a node rest api reply to a transaction object
        """
        # here is the case of a api get, that is a GenericSingedTx
        # decode the object o a dictionary
        return self._jsontx_to_txobject(tx_data)

    def parse_tx_string(self, tx_string) -> TxObject:
        """
        Parse a transaction string to a transaction object
        """
        # it is an encoded tx, happens when there is a tx to decode
        rlp_data = decode(tx_string)
        return self._rlptx_to_txobject(rlp_data)

    def tx_signed(self, signatures: list, tx: TxObject, metadata={}):
        """
        Create a signed transaction. This is a special type of transaction
        as it wraps a normal transaction adding one or more signature
        """
        body = dict(
            tag=idf.OBJECT_TAG_SIGNED_TRANSACTION,
            version=idf.VSN,
            signatures=signatures,
            tx=tx
        )
        return self._build_txobject(body, metadata=metadata)

    def tx_spend(self, sender_id, recipient_id, amount, payload, fee, ttl, nonce) -> TxObject:
        """
        create a spend transaction
        :param sender_id: the public key of the sender
        :param recipient_id: the public key of the recipient
        :param amount: the amount to send
        :param payload: the payload associated with the data
        :param fee: the fee for the transaction
        :param ttl: the absolute ttl of the transaction
        :param nonce: the nonce of the transaction
        """
        # use internal endpoints transaction
        body = dict(
            tag=idf.OBJECT_TAG_SPEND_TRANSACTION,
            version=idf.VSN,
            recipient_id=recipient_id,
            amount=amount,
            fee=fee,
            sender_id=sender_id,
            payload=encode(idf.BYTE_ARRAY, payload),
            ttl=ttl,
            nonce=nonce,
        )
        return self._build_txobject(body)
        # return self.api.post_spend(body=body).tx

    # NAMING #

    def tx_name_preclaim(self, account_id, commitment_id, fee, ttl, nonce) -> TxObject:
        """
        create a preclaim transaction
        :param account_id: the account registering the name
        :param commitment_id: the commitment id
        :param fee:  the fee for the transaction
        :param ttl:  the ttl for the transaction
        :param nonce: the nonce of the account for the transaction
        """
        body = dict(
            tag=idf.OBJECT_TAG_NAME_SERVICE_PRECLAIM_TRANSACTION,
            version=idf.VSN,
            commitment_id=commitment_id,
            fee=fee,
            account_id=account_id,
            ttl=ttl,
            nonce=nonce
        )
        return self._build_txobject(body)
        # return self.api.post_name_preclaim(body=body).tx

    def tx_name_claim(self, account_id, name, name_salt, fee, ttl, nonce) -> TxObject:
        """
        create a preclaim transaction
        :param account_id: the account registering the name
        :param name: the actual name to claim
        :param name_salt: the salt used to create the commitment_id during preclaim
        :param fee:  the fee for the transaction
        :param ttl:  the ttl for the transaction
        :param nonce: the nonce of the account for the transaction
        """
        body = dict(
            tag=idf.OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION,
            version=idf.VSN,
            account_id=account_id,
            name=name,
            name_salt=name_salt,
            fee=fee,
            ttl=ttl,
            nonce=nonce
        )
        return self._build_txobject(body)

    def tx_name_claim_v2(self, account_id, name, name_salt, name_fee, fee, ttl, nonce) -> TxObject:
        """
        create a preclaim transaction
        :param account_id: the account registering the name
        :param name: the actual name to claim
        :param name_salt: the salt used to create the commitment_id during preclaim
        :param name_fee: the fee bid to claim the name
        :param fee:  the fee for the transaction
        :param ttl:  the ttl for the transaction
        :param nonce: the nonce of the account for the transaction
        """
        body = dict(
            tag=idf.OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION,
            version=2,
            account_id=account_id,
            name=name,
            name_salt=name_salt,
            name_fee=name_fee,
            fee=fee,
            ttl=ttl,
            nonce=nonce
        )
        return self._build_txobject(body)

    def tx_name_update(self, account_id, name_id, pointers, name_ttl, client_ttl, fee, ttl, nonce) -> TxObject:
        """
        create an update transaction
        :param account_id: the account updating the name
        :param name_id: the name id
        :param pointers:  the pointers to update to
        :param name_ttl:  the ttl for the name registration
        :param client_ttl:  the ttl for client to cache the name
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        :param nonce: the nonce of the account for the transaction
        """
        body = dict(
            tag=idf.OBJECT_TAG_NAME_SERVICE_UPDATE_TRANSACTION,
            version=idf.VSN,
            account_id=account_id,
            name_id=name_id,
            client_ttl=client_ttl,
            name_ttl=name_ttl,
            pointers=pointers,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        return self._build_txobject(body)
        # return self.api.post_name_update(body=body).tx

    def tx_name_transfer(self, account_id, name_id, recipient_id, fee, ttl, nonce) -> TxObject:
        """
        create a transfer transaction
        :param account_id: the account transferring the name
        :param name_id: the name to transfer
        :param recipient_id: the address of the account to transfer the name to
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        :param nonce: the nonce of the account for the transaction
        """
        body = dict(
            tag=idf.OBJECT_TAG_NAME_SERVICE_TRANSFER_TRANSACTION,
            version=idf.VSN,
            account_id=account_id,
            name_id=name_id,
            recipient_id=recipient_id,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        return self._build_txobject(body)
        # return self.api.post_name_transfer(body=body).tx

    def tx_name_revoke(self, account_id, name_id, fee, ttl, nonce) -> TxObject:
        """
        create a revoke transaction
        :param account_id: the account revoking the name
        :param name_id: the name to revoke
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        :param nonce: the nonce of the account for the transaction
        """

        body = dict(
            tag=idf.OBJECT_TAG_NAME_SERVICE_REVOKE_TRANSACTION,
            version=idf.VSN,
            account_id=account_id,
            name_id=name_id,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        return self._build_txobject(body)
        # return self.api.post_name_revoke(body=body).tx

    # CONTRACTS

    def tx_contract_create(self, owner_id, code, call_data, amount, deposit, gas, gas_price, vm_version, abi_version, fee, ttl, nonce) -> TxObject:
        """
        Create a contract transaction
        :param owner_id: the account creating the contract
        :param code: the binary code of the contract
        :param call_data: the call data for the contract
        :param amount: initial amount(balance) of the contract
        :param deposit: the deposit bound to the contract
        :param gas: the gas limit for the execution of the limit function
        :param gas_price: the gas price for the unit of gas
        :param vm_version: the vm version of the contract
        :param abi_version: TODO: add definition
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        :param nonce: the nonce of the account for the transaction
        """
        body = dict(
            tag=idf.OBJECT_TAG_CONTRACT_CREATE_TRANSACTION,
            version=idf.VSN,
            owner_id=owner_id,
            amount=amount,
            deposit=deposit,
            fee=fee,
            gas=gas,
            gas_price=gas_price,
            vm_version=vm_version,
            abi_version=abi_version,
            call_data=call_data,
            code=code,
            ttl=ttl,
            nonce=nonce
        )
        return self._build_txobject(body)
        # return tx.tx, tx.contract_id

    def tx_contract_call(self, caller_id, contract_id, call_data, function, amount, gas, gas_price, abi_version, fee, ttl, nonce) -> TxObject:
        """
        Create a Contract Call transaction
        :param caller_id: the account creating the contract
        :param contract_id: the contract to call
        :param call_data: the call data for the contract
        :param function: the function to execute
        :param amount: the amount associated to the transaction call
        :param gas: the gas limit for the execution of the function
        :param gas_price: the gas unit price
        :param abi_version: TODO: add definition
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        :param nonce: the nonce of the account for the transaction
        """

        body = dict(
            tag=idf.OBJECT_TAG_CONTRACT_CALL_TRANSACTION,
            version=idf.VSN,
            call_data=call_data,
            caller_id=caller_id,
            contract_id=contract_id,
            amount=amount,
            fee=fee,
            gas=gas,
            gas_price=gas_price,
            abi_version=abi_version,
            ttl=ttl,
            nonce=nonce
        )
        return self._build_txobject(body)
        # return self.api.post_contract_call(body=body).tx

    # ORACLES

    def tx_oracle_register(self, account_id,
                           query_format, response_format,
                           query_fee, ttl_type, ttl_value, vm_version,
                           fee, ttl, nonce) -> TxObject:
        """
        Create a register oracle transaction
        """
        body = dict(
            tag=idf.OBJECT_TAG_ORACLE_REGISTER_TRANSACTION,
            version=idf.VSN,
            account_id=account_id,
            query_format=query_format,
            response_format=response_format,
            query_fee=query_fee,
            oracle_ttl_type=ttl_type,
            oracle_ttl_value=ttl_value,
            vm_version=vm_version,
            fee=fee,
            ttl=ttl,
            nonce=nonce
        )
        return self._build_txobject(body)
        # return tx.tx

    def tx_oracle_query(self, oracle_id, sender_id, query,
                        query_fee, query_ttl_type, query_ttl_value,
                        response_ttl_type, response_ttl_value,
                        fee, ttl, nonce) -> TxObject:
        """
        Create a oracle query transaction
        """

        body = dict(
            tag=idf.OBJECT_TAG_ORACLE_QUERY_TRANSACTION,
            version=idf.VSN,
            sender_id=sender_id,
            oracle_id=oracle_id,
            response_ttl_type=response_ttl_type,
            response_ttl_value=response_ttl_value,
            query=query,
            query_ttl_type=query_ttl_type,
            query_ttl_value=query_ttl_value,
            fee=fee,
            query_fee=query_fee,
            ttl=ttl,
            nonce=nonce,
        )
        return self._build_txobject(body)
        # tx = self.api.post_oracle_query(body=body)
        # return tx.tx

    def tx_oracle_respond(self, oracle_id, query_id, response,
                          response_ttl_type, response_ttl_value,
                          fee, ttl, nonce) -> TxObject:
        """
        Create a oracle response transaction
        """
        body = dict(
            tag=idf.OBJECT_TAG_ORACLE_RESPONSE_TRANSACTION,
            version=idf.VSN,
            response_ttl_type=response_ttl_type,
            response_ttl_value=response_ttl_value,
            oracle_id=oracle_id,
            query_id=query_id,
            response=response,
            fee=fee,
            ttl=ttl,
            nonce=nonce,
        )
        return self._build_txobject(body)
        # tx = self.api.post_oracle_respond(body=body)
        # return tx.tx

    def tx_oracle_extend(self, oracle_id,
                         ttl_type, ttl_value,
                         fee, ttl, nonce) -> TxObject:
        """
        Create a oracle extends transaction
        """
        body = dict(
            tag=idf.OBJECT_TAG_ORACLE_EXTEND_TRANSACTION,
            version=idf.VSN,
            oracle_id=oracle_id,
            oracle_ttl_type=ttl_type,
            oracle_ttl_value=ttl_value,
            fee=fee,
            ttl=ttl,
            nonce=nonce,
        )
        return self._build_txobject(body)
        # tx = self.api.post_oracle_extend(body=body)
        # return tx.tx

    def tx_ga_attach(self, owner_id, nonce, code,
                     auth_fun, vm_version, abi_version,
                     fee, ttl, gas, gas_price, call_data) -> TxObject:
        """
        :param owner_id: the owner of the contra
        :param nonce: the transaction nonce
        :param code: the bytecode of for the generalized account contract
        :param auth_fun: the hash of the authorization function of the ga contract
        :param vm_version: the vm version of the contract
        :param abi_version: TODO: add definition
        :param fee: the fee for the transaction
        :param ttl: the ttl for the transaction
        """
        body = dict(
            tag=idf.OBJECT_TAG_GA_ATTACH_TRANSACTION,
            version=idf.VSN,
            owner_id=owner_id,
            nonce=nonce,
            code=code,
            auth_fun=auth_fun,
            vm_version=vm_version,
            abi_version=abi_version,
            fee=fee,
            ttl=ttl,
            gas=gas,
            gas_price=gas_price,
            call_data=call_data,
        )
        return self._build_txobject(body)

    def tx_ga_meta(self, ga_id,
                   auth_data,
                   abi_version,
                   fee,
                   gas,
                   gas_price,
                   ttl,
                   tx) -> TxObject:
        """
        :param ga_id: the account id
        :param auth_data: the authorized data
        :param abi_version: compiler abi version
        :param fee: transaction fee
        :param gas: gas limit for the authorization function
        :param gas_price: the gas prize
        :param ttl: time to live (in height) of the transaction
        :param tx: the transaction to be authorized
        """
        body = dict(
            tag=idf.OBJECT_TAG_GA_META_TRANSACTION,
            version=idf.VSN,
            ga_id=ga_id,
            auth_data=auth_data,
            abi_version=abi_version,
            fee=fee,
            gas=gas,
            gas_price=gas_price,
            ttl=ttl,
            tx=tx,
        )
        return self._build_txobject(body)


class TxBuilderDebug:
    def __init__(self, api: OpenAPICli):
        """
        :param native: if the transactions should be built by the sdk (True) or requested to the debug api (False)
        """
        if api is None:
            raise ValueError("A initialized api rest client has to be provided to build a transaction using the node internal API ")
        self.api = api
