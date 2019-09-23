from aeternity.hashing import _int, _int_decode, _binary, _binary_decode, _id, _id_decode, encode, decode, decode_rlp, hash_encode
from aeternity.openapi import OpenAPICli
from aeternity import identifiers as idf
from aeternity import defaults
# from aeternity.exceptions import UnsupportedTransactionType, TransactionFeeTooLow
import rlp
import math
import pprint
import namedtupled

PACK_TX = 1
UNPACK_TX = 0

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


class Fn:
    def __init__(self, index, field_type=_INT, **kwargs):
        self.index = index
        self.field_type = field_type
        self.encoding_prefix = kwargs.get("prefix")

    def __str__(self):
        return f"{self.index}:{self.field_type}"

    def __repr__(self):
        return self.__str__()


SIZE_BASED = 0  # used for most of transactions
TTL_BASED = 1  # used for oracle
GA_META = 2  # used for meta tx


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


txf = {
    idf.OBJECT_TAG_SIGNED_TRANSACTION: {
        "fee": None,
        "schema": {
            "version": Fn(1),
            "signatures": Fn(2, _SG, prefix=idf.SIGNATURE),  # list
            "tx": Fn(3, _TX, prefix=idf.TRANSACTION),
        }
    },
    idf.OBJECT_TAG_SPEND_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "sender_id": Fn(2, _ID),
            "recipient_id": Fn(3, _ID),
            "amount": Fn(4),
            "fee": Fn(5),
            "ttl": Fn(6),
            "nonce": Fn(7),
            "payload": Fn(8, _ENC, prefix=idf.BYTE_ARRAY),
        }
    },
    idf.OBJECT_TAG_NAME_SERVICE_PRECLAIM_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "account_id": Fn(2, _ID),
            "nonce": Fn(3),
            "commitment_id": Fn(4, _ID),
            "fee": Fn(5),
            "ttl": Fn(6),
        }},
    idf.OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "account_id": Fn(2, _ID),
            "nonce": Fn(3),
            "name": Fn(4, _BIN),
            "name_salt": Fn(5),  # TODO: this has to be verified
            "fee": Fn(6),
            "ttl": Fn(7),
        }},
    idf.OBJECT_TAG_NAME_SERVICE_UPDATE_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "account_id": Fn(2, _ID),
            "nonce": Fn(3),
            "name_id": Fn(4, _ID),
            "name_ttl": Fn(5),
            "pointers": Fn(6, _PTR),
            "client_ttl": Fn(7),
            "fee": Fn(8),
            "ttl": Fn(9),
        }},
    idf.OBJECT_TAG_NAME_SERVICE_TRANSFER_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "account_id": Fn(2, _ID),
            "nonce": Fn(3),
            "name_id": Fn(4, _ID),
            "recipient_id": Fn(5, _ID),
            "fee": Fn(6),
            "ttl": Fn(7),
        }},
    idf.OBJECT_TAG_NAME_SERVICE_REVOKE_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "account_id": Fn(2, _ID),
            "nonce": Fn(3),
            "name_id": Fn(4, _ID),
            "fee": Fn(5),
            "ttl": Fn(6),
        }},
    idf.OBJECT_TAG_CONTRACT_CREATE_TRANSACTION: {
        "fee": Fee(SIZE_BASED, base_gas_multiplier=5),
        "schema": {
            "version": Fn(1),
            "owner_id": Fn(2, _ID),
            "nonce": Fn(3),
            "code": Fn(4, _ENC, prefix=idf.BYTECODE),
            # "vm_version": Fn(5),
            "abi_version": Fn(5, _VM_ABI),
            "fee": Fn(6),
            "ttl": Fn(7),
            "deposit": Fn(8),
            "amount": Fn(9),
            "gas": Fn(10),
            "gas_price": Fn(11),
            "call_data": Fn(12, _ENC, prefix=idf.BYTECODE),
        }},
    idf.OBJECT_TAG_CONTRACT_CALL_TRANSACTION: {
        "fee": Fee(SIZE_BASED, base_gas_multiplier=30),
        "schema": {
            "version": Fn(1),
            "caller_id": Fn(2, _ID),
            "nonce": Fn(3),
            "contract_id": Fn(4, _ID),
            "abi_version": Fn(5),
            "fee": Fn(6),
            "ttl": Fn(7),
            "amount": Fn(8),
            "gas": Fn(9),
            "gas_price": Fn(10),
            "call_data": Fn(11, _ENC, prefix=idf.BYTECODE),
        }},
    idf.OBJECT_TAG_CHANNEL_CREATE_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "initiator": Fn(2, _ID),
            "initiator_amount": Fn(3),
            "responder": Fn(4, _ID),
            "responder_amount": Fn(5),
            "channel_reserve": Fn(6),
            "lock_period": Fn(7),
            "ttl": Fn(8),
            "fee": Fn(9),
            "delegate_ids": Fn(10, _IDS),  # [d(d) for d in tx_native[10]], TODO: are u sure
            "state_hash": Fn(11, _ENC, prefix=idf.STATE_HASH),
            "nonce": Fn(12),
        }},
    idf.OBJECT_TAG_CHANNEL_DEPOSIT_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "channel_id": Fn(2, _ID),
            "from_id": Fn(3, _ID),
            "amount": Fn(4),
            "ttl": Fn(5),
            "fee": Fn(6),
            "state_hash": Fn(7, _ENC, prefix=idf.STATE_HASH),  # _binary_decode(tx_native[7]),
            "round": Fn(8),
            "nonce": Fn(9),
        }},
    idf.OBJECT_TAG_CHANNEL_WITHDRAW_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "channel_id": Fn(2, _ID),
            "to_id": Fn(3, _ID),
            "amount": Fn(4),
            "ttl": Fn(5),
            "fee": Fn(6),
            "state_hash": Fn(7, _ENC, prefix=idf.STATE_HASH),  # _binary_decode(tx_native[7]),
            "round": Fn(8),
            "nonce": Fn(9),
        }},
    idf.OBJECT_TAG_CHANNEL_CLOSE_MUTUAL_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "channel_id": Fn(2, _ID),
            "from_id": Fn(3, _ID),
            "initiator_amount_final": Fn(4),
            "responder_amount_final": Fn(5),
            "ttl": Fn(6),
            "fee": Fn(7),
            "nonce": Fn(8),
        }},
    idf.OBJECT_TAG_CHANNEL_CLOSE_SOLO_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "channel_id": Fn(2, _ID),
            "from_id": Fn(3, _ID),
            "payload": Fn(4, _ENC, prefix=idf.BYTE_ARRAY),
            "poi": Fn(5, _POI),
            "ttl": Fn(6),
            "fee": Fn(7),
            "nonce": Fn(8),
        }},
    idf.OBJECT_TAG_CHANNEL_SLASH_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "channel_id": Fn(2, _ID),
            "from_id": Fn(3, _ID),
            "payload": Fn(4, _ENC, prefix=idf.BYTE_ARRAY),
            "poi": Fn(5, _POI),
            "ttl": Fn(6),
            "fee": Fn(7),
            "nonce": Fn(8),
        }},
    idf.OBJECT_TAG_CHANNEL_SETTLE_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "channel_id": Fn(2, _ID),
            "from_id": Fn(3, _ID),
            "initiator_amount_final": Fn(4),
            "responder_amount_final": Fn(5),
            "ttl": Fn(6),
            "fee": Fn(7),
            "nonce": Fn(8),
        }},
    idf.OBJECT_TAG_CHANNEL_SNAPSHOT_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "channel_id": Fn(2, _ID),
            "from_id": Fn(3, _ID),
            "payload": Fn(4, _ENC, prefix=idf.BYTE_ARRAY),
            "ttl": Fn(5),
            "fee": Fn(6),
            "nonce": Fn(7),
        }},
    idf.OBJECT_TAG_CHANNEL_FORCE_PROGRESS_TRANSACTION: {
        "fee": Fee(SIZE_BASED),
        "schema": {
            "version": Fn(1),
            "channel_id": Fn(2, _ID),
            "from_id": Fn(3, _ID),
            "payload": Fn(4, _ENC, prefix=idf.BYTE_ARRAY),
            "round": Fn(5),
            "update": Fn(6),  # _binary_decode(tx_native[2]),
            "state_hash": Fn(7, _ENC, prefix=idf.STATE_HASH),  # _binary_decode(tx_native[2]),
            "offchain_trees": Fn(8, _TR),  # TODO: implement support for _trees
            "ttl": Fn(2),
            "fee": Fn(2),
            "nonce": Fn(2),
        }},
    idf.OBJECT_TAG_ORACLE_REGISTER_TRANSACTION: {
        "fee": Fee(TTL_BASED, ttl_field="oracle_ttl_value"),
        "schema": {
            "version": Fn(1),
            "account_id": Fn(2, _ID),
            "nonce": Fn(3),
            "query_format": Fn(4, _BIN),  # _binary_decode(tx_native[4]), TODO: verify the type
            "response_format": Fn(5, _BIN),  # _binary_decode(tx_native[5]),
            "query_fee": Fn(6),
            "oracle_ttl_type": Fn(7, _OTTL_TYPE),
            "oracle_ttl_value": Fn(8),
            "fee": Fn(9),
            "ttl": Fn(10),
            "vm_version": Fn(11),
        }},
    idf.OBJECT_TAG_ORACLE_QUERY_TRANSACTION: {
        "fee": Fee(TTL_BASED, ttl_field="query_ttl_value"),
        "schema": {
            "version": Fn(1),
            "sender_id": Fn(2, _ID),
            "nonce": Fn(3),
            "oracle_id": Fn(4, _ID),
            "query": Fn(5, _BIN),
            "query_fee": Fn(6),
            "query_ttl_type": Fn(7, _OTTL_TYPE),
            "query_ttl_value": Fn(8),
            "response_ttl_type": Fn(9, _OTTL_TYPE),
            "response_ttl_value": Fn(10),
            "fee": Fn(11),
            "ttl": Fn(12),
        }},
    idf.OBJECT_TAG_ORACLE_RESPONSE_TRANSACTION: {
        "fee": Fee(TTL_BASED, ttl_field="response_ttl_value"),
        "schema": {
            "version": Fn(1),
            "oracle_id": Fn(2, _ID),
            "nonce": Fn(3),
            "query_id": Fn(4, _ENC, prefix=idf.ORACLE_QUERY_ID),
            "response": Fn(5, _BIN),
            "response_ttl_type": Fn(6, _OTTL_TYPE),
            "response_ttl_value": Fn(7),
            "fee": Fn(8),
            "ttl": Fn(9),
        }},
    idf.OBJECT_TAG_ORACLE_EXTEND_TRANSACTION: {
        "fee": Fee(TTL_BASED, ttl_field="oracle_ttl_value"),
        "schema": {
            "version": Fn(1),
            "oracle_id": Fn(2, _ID),
            "nonce": Fn(3),
            "oracle_ttl_type": Fn(4, _OTTL_TYPE),
            "oracle_ttl_value": Fn(5),
            "fee": Fn(6),
            "ttl": Fn(7),
        }},
    idf.OBJECT_TAG_GA_ATTACH_TRANSACTION: {
        "fee": Fee(SIZE_BASED, base_gas_multiplier=5),
        "schema": {
            "version": Fn(1),
            "owner_id": Fn(2, _ID),
            "nonce": Fn(3),
            "code": Fn(4, _ENC, prefix=idf.BYTECODE),
            "auth_fun": Fn(5, _BIN),
            # "vm_version": Fn(6), # This field is retrieved via abi_version
            "abi_version": Fn(6, _VM_ABI),
            "fee": Fn(7),
            "ttl": Fn(8),
            "gas": Fn(9),
            "gas_price": Fn(10),
            "call_data": Fn(11, _ENC, prefix=idf.BYTECODE),  # _binary_decode(tx_native[11]),
        }},
    idf.OBJECT_TAG_GA_META_TRANSACTION: {
        "fee": Fee(SIZE_BASED, base_gas_multiplier=5),
        "schema": {
            "version": Fn(1),
            "ga_id": Fn(2, _ID),
            "auth_data": Fn(3, _ENC, prefix=idf.BYTECODE),
            "abi_version": Fn(4),
            "fee": Fn(5),
            "gas": Fn(6),
            "gas_price": Fn(7),
            "ttl": Fn(8),
            "tx": Fn(9, _TX),
        }
    },
}


class TxObject:
    """
    This is a TxObject that is used throughout the SDK for transactions
    It contains all the info associated to a transaction like transaction data,transaction hash, etx

    """

    def __init__(self, **kwargs):
        self.data = kwargs.get("data", None)
        self.tx = kwargs.get("tx", None)
        self.hash = kwargs.get("hash", None)
        self.metadata = kwargs.get("metadata", None)
        self.network_id = kwargs.get("network_id", None)
        self.signatures = kwargs.get("signatures", [])

    def asdict(self):
        t = dict(
            data=namedtupled.reduce(self.data),
            metadata=self.metadata,
            tx=self.tx,
            hash=self.hash
        )
        if "tx" in t.get("data", {}):
            t["data"]["tx"] = t["data"]["tx"].asdict()

        return t

    def get_signatures(self):
        """
        retrieves the list of signatures for a signed transaction, otherwhise returns a empty list
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
            raise TypeError(f"there is no signaure at index {index}")
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

    def cosign_encode_transaction(self, tx): # TODO: remove this function
        # decode the transaction if not in native mode
        transaction = None  #_tx_native(op=UNPACK_TX, tx=tx.tx if hasattr(tx, "tx") else tx)
        # get the transaction as bytes
        tx_raw = decode(transaction.data.tx)
        # sign the transaction
        signatures = transaction.data.signatures + [encode(idf.SIGNATURE, self.account.sign(_binary(self.network_id) + tx_raw))]
        body = dict(
            tag=idf.OBJECT_TAG_SIGNED_TRANSACTION,
            signatures=signatures,
            tx=transaction.data.tx
        )
        return None

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
        pass

    @staticmethod
    def compute_tx_hash(encoded_tx: str) -> str:
        """
        Generate the hash from a signed and encoded transaction
        :param encoded_tx: an encoded signed transaction
        """
        tx_raw = decode(encoded_tx)
        return hash_encode(idf.TRANSACTION_HASH, tx_raw)

    def compute_min_fee(self, tx_data: dict, tx_descriptor: dict, tx_raw: list):
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

    def _apiget_to_tobject(self, api_data):
        # TODO: compute also the min_fee
        tx_data = namedtupled.reduce(api_data)
        if "signatures" in tx_data:
            tx_data["tag"] = idf.OBJECT_TAG_SIGNED_TRANSACTION
            # signed tx, extract the inner tx
            # TODO: this should be a tobject in the data
            tx_data["tx"] = encode(idf.TRANSACTION, self._apiget_to_tobject(api_data.tx))
        tx_data["tag"] = idf.TRANSACTION_TYPE_TO_TAG.get(api_data.type)
        # encode th tx in rlp
        raw = self._params_to_api(tx_data, txf.get(tx_data.get("tag", {})).get("schema"))
        rlp_tx = rlp.encode(raw)
        # encode the tx in base64
        rlp_b64_tx = encode(idf.TRANSACTION, rlp_tx)
        # compute the tx hash
        tx_hash = hash_encode(idf.TRANSACTION_HASH, rlp_tx)
        # now build the tx object
        return TxObject(
            metadata=namedtupled.map({}, _nt_name="TxMeta"),
            data=namedtupled.map(tx_data, _nt_name="TxData"),
            tx=rlp_b64_tx,
            hash=tx_hash
        )
        return

    def _params_to_api(self, data: dict, schema: dict) -> TxObject:
        # initialize the right data size
        # this is PYTHON to POSTBODY
        raw_data = [0] * (len(schema) + 1)  # the +1 is for the tag
        # set the tx tag first
        raw_data[0] = _int(data.get("tag"))
        # parse fields and encode them
        for label, fn in schema.items():
            if fn.field_type == _INT:
                raw_data[fn.index] = _int(data.get(label))
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
        return raw_data

    def _api_to_params(self, raw):
        # this is POSTBODY to TObject
        # takes in an unserialized rlp object
        tag = _int_decode(raw[0])
        # TODO: verify that the schema is there
        schema = txf.get(tag, {}).get("schema")
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
                # this are byte arrays, TODO: should add type
                tx_data[label] = _binary_decode(raw[fn.index])
            elif fn.field_type == _PTR:
                # this are name pointers
                tx_data[label] = [{"key": _binary_decode(p[0], data_type=str), "id": _id_decode(p[1])} for p in raw[fn.index]]
            elif fn.field_type == _TX:
                # this can be raw or tx object
                tx_data[label] = self._api_to_params(rlp.decode(raw[fn.index]))
        # encode th tx in rlp
        rlp_tx = rlp.encode(raw)
        # encode the tx in base64
        rlp_b64_tx = encode(idf.TRANSACTION, rlp_tx)
        # compute the tx hash
        tx_hash = hash_encode(idf.TRANSACTION_HASH, rlp_tx)
        # now build the tx object
        return TxObject(
            metadata=namedtupled.map({}, _nt_name="TxMeta"),
            data=namedtupled.map(tx_data, _nt_name="TxData"),
            tx=rlp_b64_tx,
            hash=tx_hash
        )

    def _build_tx_object(self, tx_data, metadata={}):
        # tree cases here
        # 1. (namedtuple) from api queries so everything is wrapped around a json object that is a  generic signed transaction
        # 2. (string) from and b64c enocoded rlp tx
        # 3. (dict) from functions of this class
        if isinstance(tx_data, str):
            # it is an encoded tx, happens when there is a tx to decode
            raw = decode_rlp(tx_data)
            return self._api_to_params(raw)
        if hasattr(tx_data, "block_height"):
            # her is the case of a api get, that is a GenericSingedTx
            # decode the object o a dictionary
            return self._apiget_to_tobject(tx_data)
        # if it comes from an api request it will not have the tag but the type
        tag = tx_data.get("tag")
        if tag is None:
            # see if the there is a type in the transaction that matches
            # the tx types from the API
            tag = idf.TRANSACTION_TYPE_TO_TAG.get(tx_data.get("type", "Unknown"), -1)
        # check if we have something
        tx_descriptor = txf.get(tag)
        if tx_descriptor is None:
            # the transaction is not defined
            raise TypeError(f"Unknown transaction tag {tag}")
        # this will return an object that can be encoded in rlp
        raw = self._params_to_api(tx_data, tx_descriptor.get("schema"))
        # now we can compute the minimum fee
        metadata = metadata if metadata is not None else {}
        metadata["min_fee"] = self.compute_min_fee(tx_data, tx_descriptor, raw)
        # if the fee was set to 0 then we set the min_fee as fee
        # we use -1 as default since for the signed tx there is no field fee
        if tx_data.get("fee", -1) == 0:
            raw[tx_descriptor.get("schema").get("fee").index] = _int(metadata.get("min_fee"))
        # encode th tx in rlp
        rlp_tx = rlp.encode(raw)
        # encode the tx in base64
        rlp_b64_tx = encode(idf.TRANSACTION, rlp_tx)
        # compute the tx hash
        tx_hash = hash_encode(idf.TRANSACTION_HASH, rlp_tx)
        # now build the tx object
        return TxObject(
            metadata=namedtupled.map(metadata, _nt_name="TxMeta"),
            data=namedtupled.map(tx_data, _nt_name="TxData"),
            tx=rlp_b64_tx,
            hash=tx_hash
        )

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
        return self._build_tx_object(body, metadata=metadata)

    def tx_spend(self, sender_id, recipient_id, amount, payload, fee, ttl, nonce) -> tuple:
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
        return self._build_tx_object(body)
        # return self.api.post_spend(body=body).tx

    # NAMING #

    def tx_name_preclaim(self, account_id, commitment_id, fee, ttl, nonce) -> tuple:
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
        return self._build_tx_object(body)
        # return self.api.post_name_preclaim(body=body).tx

    def tx_name_claim(self, account_id, name, name_salt, fee, ttl, nonce) -> tuple:
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
        return self._build_tx_object(body)
        # return self.api.post_name_claim(body=body).tx

    def tx_name_update(self, account_id, name_id, pointers, name_ttl, client_ttl, fee, ttl, nonce) -> tuple:
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
        return self._build_tx_object(body)
        # return self.api.post_name_update(body=body).tx

    def tx_name_transfer(self, account_id, name_id, recipient_id, fee, ttl, nonce) -> tuple:
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
        return self._build_tx_object(body)
        # return self.api.post_name_transfer(body=body).tx

    def tx_name_revoke(self, account_id, name_id, fee, ttl, nonce) -> tuple:
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
        return self._build_tx_object(body)
        # return self.api.post_name_revoke(body=body).tx

    # CONTRACTS

    def tx_contract_create(self, owner_id, code, call_data, amount, deposit, gas, gas_price, vm_version, abi_version, fee, ttl, nonce) -> tuple:
        """
        Create a contract transaction
        :param owner_id: the account creating the contract
        :param code: the binary code of the contract
        :param call_data: the call data for the contract
        :param amount: initial amount(balance) of the contract
        :param deposit: TODO: add definition
        :param gas: TODO: add definition
        :param gas_price: TODO: add definition
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
        return self._build_tx_object(body)
        # return tx.tx, tx.contract_id

    def tx_contract_call(self, caller_id, contract_id, call_data, function, arg, amount, gas, gas_price, abi_version, fee, ttl, nonce) -> tuple:
        """
        Create a Contract Call transaction
        :param caller_id: the account creating the contract
        :param contract_id: the contract to call
        :param call_data: the call data for the contract
        :param function: the function to execute
        :param arg: the function arguments
        :param amount: TODO: add definition
        :param gas: TODO: add definition
        :param gas_price: TODO: add definition
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
        return self._build_tx_object(body)
        # return self.api.post_contract_call(body=body).tx

    # ORACLES

    def tx_oracle_register(self, account_id,
                           query_format, response_format,
                           query_fee, ttl_type, ttl_value, vm_version,
                           fee, ttl, nonce) -> tuple:
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
        return self._build_tx_object(body)
        # return tx.tx

    def tx_oracle_query(self, oracle_id, sender_id, query,
                        query_fee, query_ttl_type, query_ttl_value,
                        response_ttl_type, response_ttl_value,
                        fee, ttl, nonce) -> tuple:
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
        return self._build_tx_object(body)
        # tx = self.api.post_oracle_query(body=body)
        # return tx.tx

    def tx_oracle_respond(self, oracle_id, query_id, response,
                          response_ttl_type, response_ttl_value,
                          fee, ttl, nonce) -> tuple:
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
        return self._build_tx_object(body)
        # tx = self.api.post_oracle_respond(body=body)
        # return tx.tx

    def tx_oracle_extend(self, oracle_id,
                         ttl_type, ttl_value,
                         fee, ttl, nonce) -> tuple:
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
        return self._build_tx_object(body)
        # tx = self.api.post_oracle_extend(body=body)
        # return tx.tx

    def tx_ga_attach(self, owner_id, nonce, code,
                     auth_fun, vm_version, abi_version,
                     fee, ttl, gas, gas_price, call_data):
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
        return self._build_tx_object(body)

    def tx_ga_meta(self, ga_id,
                   auth_data,
                   abi_version,
                   fee,
                   gas,
                   gas_price,
                   ttl,
                   tx):
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
        return self._build_tx_object(body)


class TxBuilderDebug:
    def __init__(self, api: OpenAPICli):
        """
        :param native: if the transactions should be built by the sdk (True) or requested to the debug api (False)
        """
        if api is None:
            raise ValueError("A initialized api rest client has to be provided to build a transaction using the node internal API ")
        self.api = api
