from aeternity.hashing import _int, _int_decode, _binary, _binary_decode, _id, _id_decode, encode, decode, encode_rlp, decode_rlp, hash_encode
from aeternity.openapi import OpenAPICli
from aeternity import identifiers as idf
from aeternity import defaults
from aeternity.exceptions import UnsupportedTransactionType, TransactionFeeTooLow
import rlp
import math
import namedtupled

PACK_TX = 1
UNPACK_TX = 0

tx_fields_index = {
    idf.OBJECT_TAG_SPEND_TRANSACTION: {
        "sender_id": 2,
        "recipient_id": 3,
        "amount": 4,
        "fee": 5,
        "ttl": 6,
        "nonce": 7,
        "payload": 8,
    }
}


def _field_idx(object_tag: int, field_name: str) -> int:
    if field_name == "tag":
        return 0
    if field_name == "vsn":
        return 1
    o = tx_fields_index.get(object_tag)
    if o is None:
        raise ValueError(f"Unrecognized object tag {object_tag}")
    idx = o.get(field_name)
    if idx is None:
        raise ValueError(f"Unrecognized field {field_name} for object tag {object_tag}")
    return idx


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

    def cosign_encode_transaction(self, tx):
        # decode the transaction if not in native mode
        transaction = _tx_native(op=UNPACK_TX, tx=tx.tx if hasattr(tx, "tx") else tx)
        # get the transaction as bytes
        tx_raw = decode(transaction.data.tx)
        # sign the transaction
        signatures = transaction.data.signatures + [encode(idf.SIGNATURE, self.account.sign(_binary(self.network_id) + tx_raw))]
        body = dict(
            tag=idf.OBJECT_TAG_SIGNED_TRANSACTION,
            signatures=signatures,
            tx=transaction.data.tx
        )
        return _tx_native(op=PACK_TX, **body)

    def sign_encode_transaction(self, tx, metadata: dict = None):
        """
        Sign, encode and compute the hash of a transaction
        :param tx: the TxObject to be signed
        :param metadata: additional data to include in the output of the signed transaction object
        :return: encoded_signed_tx, encoded_signature, tx_hash
        """
        # TODO: handle here GA transactions
        # decode the transaction if not in native mode
        transaction = _tx_native(op=UNPACK_TX, tx=tx.tx if hasattr(tx, "tx") else tx)
        # get the transaction as byte list
        tx_raw = decode(transaction.tx)
        # sign the transaction
        signature = self.account.sign(_binary(self.network_id) + tx_raw)
        # pack and encode the transaction
        tx_body = dict(
            tag=idf.OBJECT_TAG_SIGNED_TRANSACTION,
            signatures=[encode(idf.SIGNATURE, signature)],
            tx=transaction.tx
        )
        packed_tx = _tx_native(op=PACK_TX, **tx_body)
        # compute the hash
        tx_hash = TxBuilder.compute_tx_hash(packed_tx.tx)
        # return the object
        tx = dict(
            data=transaction.data,
            metadata=metadata,
            tx=packed_tx.tx,
            hash=tx_hash,
            signature=packed_tx.data.signatures,
            network_id=self.network_id,
        )
        return namedtupled.map(tx, _nt_name="TxObject")


def _tx_native(op, **kwargs):

    def std_fee(tx_raw, fee_idx, base_gas_multiplier=1):
        # calculates the standard minimum transaction fee
        tx_copy = tx_raw  # create a copy of the input
        actual_fee = 0
        tx_copy[fee_idx] = _int(actual_fee)  # replace fee with a byte array of length 1
        expected = (defaults.BASE_GAS * base_gas_multiplier + len(rlp.encode(tx_copy)) * defaults.GAS_PER_BYTE) * defaults.GAS_PRICE
        while expected != actual_fee:
            actual_fee = expected
            tx_copy[fee_idx] = _int(expected)
            expected = (defaults.BASE_GAS * base_gas_multiplier + len(rlp.encode(tx_copy)) * defaults.GAS_PER_BYTE) * defaults.GAS_PRICE
        return actual_fee

    def oracle_fee(tx_raw, fee_idx, relative_ttl):
        # estimate oracle fees
        tx_copy = tx_raw  # create a copy of the input
        actual_fee = 0
        tx_copy[fee_idx] = _int(actual_fee)  # replace fee with a byte array of length 1
        ttl_cost = math.ceil(32000 * relative_ttl / math.floor(60 * 24 * 365 / defaults.KEY_BLOCK_INTERVAL))  # calculate the variable cost for ttl
        expected = ((defaults.BASE_GAS + len(rlp.encode(tx_copy)) * defaults.GAS_PER_BYTE) + ttl_cost) * defaults.GAS_PRICE
        while expected != actual_fee:
            actual_fee = expected
            tx_copy[fee_idx] = _int(expected)
            expected = ((defaults.BASE_GAS + len(rlp.encode(tx_copy)) * defaults.GAS_PER_BYTE) + ttl_cost) * defaults.GAS_PRICE
        return actual_fee

    def build_tx_object(tx_data, tx_raw, fee_idx=None, min_fee=None):
        # if there are fee involved verify the fee
        if min_fee is not None and fee_idx is not None:
            # if fee is not set use the min fee
            if tx_data.get("fee") <= 0:
                tx_data["fee"] = min_fee
            # if it is set check that is greater then the minimum fee
            elif tx_data.get("fee") < min_fee:
                raise TransactionFeeTooLow(f'Minimum transaction fee is {min_fee}, provided fee is {tx_data.get("fee")}')
            tx_native[fee_idx] = _int(tx_data.get("fee"))
        # create the transaction object
        tx_encoded = encode_rlp(idf.TRANSACTION, tx_native)
        tx = dict(
            data=tx_data,
            tx=tx_encoded,
            hash=TxBuilder.compute_tx_hash(tx_encoded),
        )
        return namedtupled.map(tx, _nt_name="TxObject")

    # prepare tag and version
    if op == PACK_TX:
        tag = kwargs.get("tag", 0)
        vsn = kwargs.get("vsn", idf.VSN)
        tx_data = kwargs
    elif op == UNPACK_TX:
        tx_native = decode_rlp(kwargs.get("tx", []))
        tag = _int_decode(tx_native[0])
    else:
        raise Exception("Invalid operation")

    # check the tags
    if tag == idf.OBJECT_TAG_SIGNED_TRANSACTION:
        # this is a bit of a special case since there is no fee
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                [decode(x) for x in kwargs.get("signatures", [])],
                decode(kwargs.get("tx"))
            ]
        elif op == UNPACK_TX:
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                signatures=[encode(idf.SIGNATURE, sg) for sg in tx_native[2]],
                tx=encode(idf.TRANSACTION, tx_native[3]),
            )
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native)
    elif tag == idf.OBJECT_TAG_SPEND_TRANSACTION:
        tx_field_fee_index = 5
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("sender_id")),
                _id(kwargs.get("recipient_id")),
                _int(kwargs.get("amount")),
                _int(kwargs.get("fee")),  # index 5
                _int(kwargs.get("ttl")),
                _int(kwargs.get("nonce")),
                _binary(kwargs.get("payload"))
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                sender_id=_id_decode(tx_native[2]),
                recipient_id=_id_decode(tx_native[3]),
                amount=_int_decode(tx_native[4]),
                fee=_int_decode(tx_native[5]),
                ttl=_int_decode(tx_native[6]),
                nonce=_int_decode(tx_native[7]),
                payload=encode(idf.BYTE_ARRAY, tx_native[8]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_NAME_SERVICE_PRECLAIM_TRANSACTION:
        tx_field_fee_index = 5
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("account_id")),
                _int(kwargs.get("nonce")),
                _id(kwargs.get("commitment_id")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl"))
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                account_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                commitment_id=_id_decode(tx_native[4]),
                fee=_int_decode(tx_native[5]),
                ttl=_int_decode(tx_native[6]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION:
        tx_field_fee_index = 6
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("account_id")),
                _int(kwargs.get("nonce")),
                _binary(kwargs.get("name")),
                _binary(kwargs.get("name_salt")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl"))
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                account_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                name=_binary_decode(tx_native[4], str),
                name_salt=_binary_decode(tx_native[5], int),
                fee=_int_decode(tx_native[6]),
                ttl=_int_decode(tx_native[7]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_NAME_SERVICE_UPDATE_TRANSACTION:
        tx_field_fee_index = 8
        if op == PACK_TX:  # pack transaction
            # first assemble the pointers
            def pointer_tag(pointer):
                return {
                    "account_pubkey": idf.ID_TAG_ACCOUNT,
                    "oracle_pubkey": idf.ID_TAG_ORACLE,
                    "contract_pubkey": idf.ID_TAG_CONTRACT,
                    "channel_pubkey": idf.ID_TAG_CHANNEL
                }.get(pointer.get("key"))
            ptrs = [[_binary(p.get("key")), _id(p.get("id"))] for p in kwargs.get("pointers", [])]
            # then build the transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("account_id")),
                _int(kwargs.get("nonce")),
                _id(kwargs.get("name_id")),
                _int(kwargs.get("name_ttl")),
                ptrs,
                _int(kwargs.get("client_ttl")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl"))
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                account_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                name=_id_decode(tx_native[4]),
                name_ttl=_int_decode(tx_native[5]),
                pointers=[],  # TODO: decode pointers
                client_ttl=_int_decode(tx_native[7]),
                fee=_int_decode(tx_native[8]),
                ttl=_int_decode(tx_native[9]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_NAME_SERVICE_TRANSFER_TRANSACTION:
        tx_field_fee_index = 6
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("account_id")),
                _int(kwargs.get("nonce")),
                _id(kwargs.get("name_id")),
                _id(kwargs.get("recipient_id")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                account_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                name=_id_decode(tx_native[4]),
                recipient_id=_id_decode(tx_native[5]),
                fee=_int_decode(tx_native[6]),
                ttl=_int_decode(tx_native[7]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_NAME_SERVICE_REVOKE_TRANSACTION:
        tx_field_fee_index = 5
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("account_id")),
                _int(kwargs.get("nonce")),
                _id(kwargs.get("name_id")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                account_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                name=_id_decode(tx_native[4]),
                fee=_int_decode(tx_native[5]),
                ttl=_int_decode(tx_native[6]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_CONTRACT_CREATE_TRANSACTION:
        tx_field_fee_index = 6
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("owner_id")),
                _int(kwargs.get("nonce")),
                _binary(decode(kwargs.get("code"))),
                _int(kwargs.get("vm_version")) + _int(kwargs.get("abi_version"), 2),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl")),
                _int(kwargs.get("deposit")),
                _int(kwargs.get("amount")),
                _int(kwargs.get("gas")),
                _int(kwargs.get("gas_price")),
                _binary(decode(kwargs.get("call_data"))),
            ]
            # TODO: verify the fee calculation for the contract
            min_fee = std_fee(tx_native, tx_field_fee_index,  base_gas_multiplier=5)
        elif op == UNPACK_TX:  # unpack transaction
            vml = len(tx_native[5])  # this is used to extract the abi and vm version from the 5th field
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                owner_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                code=encode(idf.BYTECODE, tx_native[4]),
                vm_version=_int_decode(tx_native[5][0:vml - 2]),
                abi_version=_int_decode(tx_native[5][vml - 2:]),
                fee=_int_decode(tx_native[6]),
                ttl=_int_decode(tx_native[7]),
                deposit=_int_decode(tx_native[8]),
                amount=_int_decode(tx_native[9]),
                gas=_int_decode(tx_native[10]),
                gas_price=_int_decode(tx_native[11]),
                call_data=encode(idf.BYTECODE, tx_native[12]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_CONTRACT_CALL_TRANSACTION:
        tx_field_fee_index = 6
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("caller_id")),
                _int(kwargs.get("nonce")),
                _id(kwargs.get("contract_id")),
                _int(kwargs.get("abi_version")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl")),
                _int(kwargs.get("amount")),
                _int(kwargs.get("gas")),
                _int(kwargs.get("gas_price")),
                decode(kwargs.get("call_data")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index, base_gas_multiplier=30)
        elif op == UNPACK_TX:  # unpack transaction
            vml = len(tx_native[5])  # this is used to extract the abi and vm version from the 5th field
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                caller_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                contract_id=_id_decode(tx_native[4]),
                abi_version=_int_decode(tx_native[5]),
                fee=_int_decode(tx_native[6]),
                ttl=_int_decode(tx_native[7]),
                amount=_int_decode(tx_native[8]),
                gas=_int_decode(tx_native[9]),
                gas_price=_int_decode(tx_native[10]),
                call_data=encode(idf.BYTECODE, tx_native[11]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_CHANNEL_CREATE_TRANSACTION:
        tx_field_fee_index = 9
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("initiator")),
                _int(kwargs.get("initiator_amount")),
                _id(kwargs.get("responder")),
                _int(kwargs.get("responder_amount")),
                _int(kwargs.get("channel_reserve")),
                _int(kwargs.get("lock_period")),
                _int(kwargs.get("ttl")),
                _int(kwargs.get("fee")),
                [_id(d) for d in kwargs.get("delegate_ids", [])],
                _binary(kwargs.get("state_hash")),
                _int(kwargs.get("nonce")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                initiator=_id_decode(tx_native[2]),
                initiator_amount=_int_decode(tx_native[3]),
                responder=_id_decode(tx_native[4]),
                responder_amount=_int_decode(tx_native[5]),
                channel_reserve=_int_decode(tx_native[6]),
                lock_period=_int_decode(tx_native[7]),
                ttl=_int_decode(tx_native[8]),
                fee=_int_decode(tx_native[9]),
                delegate_ids=[_id_decode(d) for d in tx_native[10]],
                state_hash=encode(idf.STATE, tx_native[11]),
                nonce=_int_decode(tx_native[12]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_CHANNEL_DEPOSIT_TRANSACTION:
        tx_field_fee_index = 6
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("channel_id")),
                _id(kwargs.get("from_id")),
                _int(kwargs.get("amount")),
                _int(kwargs.get("ttl")),
                _int(kwargs.get("fee")),
                _binary(kwargs.get("state_hash")),
                _int(kwargs.get("round")),
                _int(kwargs.get("nonce")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                channel_id=_id_decode(tx_native[2]),
                from_id=_id_decode(tx_native[3]),
                amount=_int_decode(tx_native[4]),
                ttl=_int_decode(tx_native[5]),
                fee=_int_decode(tx_native[6]),
                state_hash=_binary_decode(tx_native[7]),
                round=_int_decode(tx_native[8]),
                nonce=_int_decode(tx_native[9]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_CHANNEL_WITHDRAW_TRANSACTION:
        tx_field_fee_index = 6
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("channel_id")),
                _id(kwargs.get("to_id")),
                _int(kwargs.get("amount")),
                _int(kwargs.get("ttl")),
                _int(kwargs.get("fee")),
                _binary(kwargs.get("state_hash")),
                _int(kwargs.get("round")),
                _int(kwargs.get("nonce")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                channel_id=_id_decode(tx_native[2]),
                to_id=_id_decode(tx_native[3]),
                amount=_int_decode(tx_native[4]),
                ttl=_int_decode(tx_native[5]),
                fee=_int_decode(tx_native[6]),
                state_hash=_binary_decode(tx_native[7]),
                round=_int_decode(tx_native[8]),
                nonce=_int_decode(tx_native[9]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_CHANNEL_CLOSE_MUTUAL_TRANSACTION:
        tx_field_fee_index = 7
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("channel_id")),
                _id(kwargs.get("from_id")),
                _int(kwargs.get("initiator_amount_final")),
                _int(kwargs.get("responder_amount_final")),
                _int(kwargs.get("ttl")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("nonce")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                channel_id=_id_decode(tx_native[2]),
                from_id=_id_decode(tx_native[3]),
                initiator_amount_final=_int_decode(tx_native[4]),
                responder_amount_final=_int_decode(tx_native[5]),
                ttl=_int_decode(tx_native[6]),
                fee=_int_decode(tx_native[7]),
                nonce=_int_decode(tx_native[8]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_CHANNEL_CLOSE_SOLO_TRANSACTION:
        tx_field_fee_index = 7
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("channel_id")),
                _id(kwargs.get("from_id")),
                _binary(kwargs.get("payload")),
                # _poi(kwargs.get("poi")), TODO: implement support for _poi
                _int(kwargs.get("ttl")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("nonce")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                channel_id=_id_decode(tx_native[2]),
                from_id=_id_decode(tx_native[3]),
                payload=_binary_decode(tx_native[4]),
                poi=_binary_decode(tx_native[5]),
                ttl=_int_decode(tx_native[6]),
                fee=_int_decode(tx_native[7]),
                nonce=_int_decode(tx_native[8]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_CHANNEL_SLASH_TRANSACTION:
        tx_field_fee_index = 7
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("channel_id")),
                _id(kwargs.get("from_id")),
                _binary(kwargs.get("payload")),
                # _poi(kwargs.get("poi")), TODO: implement support for _poi
                _int(kwargs.get("ttl")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("nonce")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                channel_id=_id_decode(tx_native[2]),
                from_id=_id_decode(tx_native[3]),
                payload=_binary_decode(tx_native[4]),
                poi=_binary_decode(tx_native[5]),
                ttl=_int_decode(tx_native[6]),
                fee=_int_decode(tx_native[7]),
                nonce=_int_decode(tx_native[8]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_CHANNEL_SETTLE_TRANSACTION:
        tx_field_fee_index = 7
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("channel_id")),
                _id(kwargs.get("from_id")),
                _int(kwargs.get("initiator_amount_final")),
                _int(kwargs.get("responder_amount_final")),
                _int(kwargs.get("ttl")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("nonce")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                channel_id=_id_decode(tx_native[2]),
                from_id=_id_decode(tx_native[3]),
                initiator_amount_final=_int_decode(tx_native[4]),
                responder_amount_final=_int_decode(tx_native[5]),
                ttl=_int_decode(tx_native[6]),
                fee=_int_decode(tx_native[7]),
                nonce=_int_decode(tx_native[8]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_CHANNEL_SNAPSHOT_TRANSACTION:
        tx_field_fee_index = 6
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("channel_id")),
                _id(kwargs.get("from_id")),
                _binary(kwargs.get("payload")),
                _int(kwargs.get("ttl")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("nonce")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                channel_id=_id_decode(tx_native[2]),
                from_id=_id_decode(tx_native[3]),
                payload=_binary_decode(tx_native[4]),
                ttl=_int_decode(tx_native[5]),
                fee=_int_decode(tx_native[6]),
                nonce=_int_decode(tx_native[7]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_CHANNEL_FORCE_PROGRESS_TRANSACTION:
        raise Exception("Not Implemented")
        tx_field_fee_index = 9
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("channel_id")),
                _id(kwargs.get("from_id")),
                _binary(kwargs.get("payload")),
                _int(kwargs.get("round")),
                _binary(kwargs.get("update")),
                _binary(kwargs.get("state_hash")),
                # _trees(kwargs.get("offchain_trees")), TODO: implement support for _trees
                _int(kwargs.get("ttl")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("nonce")),
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                channel_id=_id_decode(tx_native[2]),
                from_id=_id_decode(tx_native[2]),
                payload=_binary_decode(tx_native[2]),
                round=_int_decode(tx_native[2]),
                update=_binary_decode(tx_native[2]),
                state_hash=_binary_decode(tx_native[2]),
                # offchain_trees=_trees_decode(tx_native[2]), TODO: implement support for _trees
                ttl=_int_decode(tx_native[2]),
                fee=_int_decode(tx_native[2]),
                nonce=_int_decode(tx_native[2]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_ORACLE_REGISTER_TRANSACTION:
        tx_field_fee_index = 9
        if op == PACK_TX:  # pack transaction
            oracle_ttl = kwargs.get("oracle_ttl", {})
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("account_id")),
                _int(kwargs.get("nonce")),
                _binary(kwargs.get("query_format")),
                _binary(kwargs.get("response_format")),
                _int(kwargs.get("query_fee")),
                _int(0 if oracle_ttl.get("type") == idf.ORACLE_TTL_TYPE_DELTA else 1),
                _int(oracle_ttl.get("value")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl")),
                _int(kwargs.get("vm_version")),
            ]
            min_fee = oracle_fee(tx_native, tx_field_fee_index, oracle_ttl.get("value"))
        elif op == UNPACK_TX:  # unpack transaction
            vml = len(tx_native[5])  # this is used to extract the abi and vm version from the 5th field
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                account_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                query_format=_binary_decode(tx_native[4]),
                response_format=_binary_decode(tx_native[5]),
                query_fee=_int_decode(tx_native[6]),
                oracle_ttl=dict(
                    type=idf.ORACLE_TTL_TYPE_DELTA if _int_decode(tx_native[7]) else idf.ORACLE_TTL_TYPE_BLOCK,
                    value=_int_decode(tx_native[8]),
                ),
                fee=_int_decode(tx_native[9]),
                ttl=_int_decode(tx_native[10]),
                vm_version=_int_decode(tx_native[11]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_ORACLE_QUERY_TRANSACTION:
        tx_field_fee_index = 11
        if op == PACK_TX:  # pack transaction
            query_ttl = kwargs.get("query_ttl", {})
            response_ttl = kwargs.get("response_ttl", {})
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("sender_id")),
                _int(kwargs.get("nonce")),
                _id(kwargs.get("oracle_id")),
                _binary(kwargs.get("query")),
                _int(kwargs.get("query_fee")),
                _int(0 if query_ttl.get("type") == idf.ORACLE_TTL_TYPE_DELTA else 1),
                _int(query_ttl.get("value")),
                _int(0 if response_ttl.get("type") == idf.ORACLE_TTL_TYPE_DELTA else 1),
                _int(response_ttl.get("value")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl")),
            ]
            min_fee = oracle_fee(tx_native, tx_field_fee_index, query_ttl.get("value"))
        elif op == UNPACK_TX:  # unpack transaction
            vml = len(tx_native[5])  # this is used to extract the abi and vm version from the 5th field
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                sender_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                oracle_id=_id_decode(tx_native[4]),
                query=_binary_decode(tx_native[5]),
                query_fee=_int_decode(tx_native[6]),
                query_ttl=dict(
                    type=idf.ORACLE_TTL_TYPE_DELTA if _int_decode(tx_native[7]) else idf.ORACLE_TTL_TYPE_BLOCK,
                    value=_int_decode(tx_native[8]),
                ),
                response_ttl=dict(
                    type=idf.ORACLE_TTL_TYPE_DELTA if _int_decode(tx_native[9]) else idf.ORACLE_TTL_TYPE_BLOCK,
                    value=_int_decode(tx_native[10]),
                ),
                fee=_int_decode(tx_native[11]),
                ttl=_int_decode(tx_native[12]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_ORACLE_RESPONSE_TRANSACTION:
        tx_field_fee_index = 8
        if op == PACK_TX:  # pack transaction
            response_ttl = kwargs.get("response_ttl", {})
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("oracle_id")),
                _int(kwargs.get("nonce")),
                decode(kwargs.get("query_id")),
                _binary(kwargs.get("response")),
                _int(0 if response_ttl.get("type") == idf.ORACLE_TTL_TYPE_DELTA else 1),
                _int(response_ttl.get("value")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl")),
            ]
            min_fee = oracle_fee(tx_native, tx_field_fee_index, response_ttl.get("value"))
        elif op == UNPACK_TX:  # unpack transaction
            vml = len(tx_native[5])  # this is used to extract the abi and vm version from the 5th field
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                oracle_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                query_id=encode(idf.ORACLE_QUERY_ID, tx_native[4]),
                response=_binary(tx_native[5]),
                response_ttl=dict(
                    type=idf.ORACLE_TTL_TYPE_DELTA if _int_decode(tx_native[6]) else idf.ORACLE_TTL_TYPE_BLOCK,
                    value=_int_decode(tx_native[7]),
                ),
                fee=_int_decode(tx_native[8]),
                ttl=_int_decode(tx_native[9]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)

    elif tag == idf.OBJECT_TAG_ORACLE_EXTEND_TRANSACTION:
        tx_field_fee_index = 6
        if op == PACK_TX:  # pack transaction
            oracle_ttl = kwargs.get("oracle_ttl", {})
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("oracle_id")),
                _int(kwargs.get("nonce")),
                _int(0 if oracle_ttl.get("type", {}) == idf.ORACLE_TTL_TYPE_DELTA else 1),
                _int(oracle_ttl.get("value")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl")),
            ]
            min_fee = oracle_fee(tx_native, tx_field_fee_index, oracle_ttl.get("value"))
        elif op == UNPACK_TX:  # unpack transaction
            vml = len(tx_native[5])  # this is used to extract the abi and vm version from the 5th field
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                oracle_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                oracle_ttl=dict(
                    type=idf.ORACLE_TTL_TYPE_DELTA if _int_decode(tx_native[4]) else idf.ORACLE_TTL_TYPE_BLOCK,
                    value=_int_decode(tx_native[5]),
                ),
                fee=_int_decode(tx_native[6]),
                ttl=_int_decode(tx_native[7]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_GA_ATTACH_TRANSACTION:
        tx_field_fee_index = 7
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("owner_id")),
                _int(kwargs.get("nonce")),
                _binary(decode(kwargs.get("code"))),
                _binary(kwargs.get("auth_fun")),
                _int(kwargs.get("vm_version")) + _int(kwargs.get("abi_version"), 2),
                _int(kwargs.get("fee")),
                _int(kwargs.get("ttl")),
                _int(kwargs.get("gas")),
                _int(kwargs.get("gas_price")),
                _binary(decode(kwargs.get("call_data"))),
            ]
            # min_fee = contract_fee(tx_native, tx_field_fee_index, kwargs.get("gas"), base_gas_multiplier=5)
            min_fee = std_fee(tx_native, tx_field_fee_index, base_gas_multiplier=5)
        elif op == UNPACK_TX:  # unpack transaction
            vml = len(tx_native[6])  # this is used to extract the abi and vm version from the 5th field
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                owner_id=_id_decode(tx_native[2]),
                nonce=_int_decode(tx_native[3]),
                code=_binary_decode(tx_native[4]),
                auth_fun=_binary_decode(tx_native[5]),
                vm_version=_int_decode(tx_native[6][0:vml - 2]),
                abi_version=_int_decode(tx_native[6][vml - 2:]),
                fee=_int_decode(tx_native[7]),
                ttl=_int_decode(tx_native[8]),
                gas=_int_decode(tx_native[9]),
                gas_price=_int_decode(tx_native[10]),
                call_data=_binary_decode(tx_native[11]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    elif tag == idf.OBJECT_TAG_GA_META_TRANSACTION:
        tx_field_fee_index = 5
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(kwargs.get("ga_id")),
                decode(kwargs.get("auth_data")),  # it should be a string: cb_XYZ
                _int(kwargs.get("abi_version")),
                _int(kwargs.get("fee")),
                _int(kwargs.get("gas")),
                _int(kwargs.get("gas_price")),
                _int(kwargs.get("ttl")),
                decode(kwargs.get("tx")),  # it should be a string: tx_XYZ
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index, base_gas_multiplier=5)
        elif op == UNPACK_TX:  # unpack transaction
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                ga_id=_id_decode(tx_native[2]),
                auth_data=encode(idf.BYTECODE, tx_native[3]),
                abi_version=_int_decode(tx_native[4]),
                fee=_int_decode(tx_native[5]),
                gas=_int_decode(tx_native[6]),
                gas_price=_int_decode(tx_native[7]),
                ttl=_int_decode(tx_native[8]),
                tx=encode(idf.TRANSACTION, tx_native[9]),
            )
            min_fee = tx_data.get("fee")
        else:
            raise Exception("Invalid operation")
        return build_tx_object(tx_data, tx_native, tx_field_fee_index, min_fee)
    else:  # unsupported tx
        raise UnsupportedTransactionType(f"Unsupported transaction tag {tag}")


class TxBuilder:
    """
    TxBuilder is used to build and post transactions to the chain.
    """

    def __init__(self):
        pass

    @staticmethod
    def compute_tx_hash(encoded_tx: str) -> str:
        """
        Generate the hash from a signed and encoded transaction
        :param encoded_tx: an encoded signed transaction
        """
        tx_raw = decode(encoded_tx)
        return hash_encode(idf.TRANSACTION_HASH, tx_raw)

    def tx_signed(self, signatures, tx):
        """
        Create a signed transaction. This is a special type of transaction
        as it wraps a normal transaction adding one or more signature
        """
        tx = tx.tx if hasattr(tx, "tx") else tx
        body = dict(
            tag=idf.OBJECT_TAG_SIGNED_TRANSACTION,
            vsn=idf.VSN,
            signatures=signatures,
            tx=tx
        )
        return _tx_native(op=PACK_TX, **body)

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
            vsn=idf.VSN,
            recipient_id=recipient_id,
            amount=amount,
            fee=fee,
            sender_id=sender_id,
            payload=payload,
            ttl=ttl,
            nonce=nonce,
        )
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
            commitment_id=commitment_id,
            fee=fee,
            account_id=account_id,
            ttl=ttl,
            nonce=nonce
        )
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
            account_id=account_id,
            name=name,
            name_salt=name_salt,
            fee=fee,
            ttl=ttl,
            nonce=nonce
        )
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
            account_id=account_id,
            name_id=name_id,
            client_ttl=client_ttl,
            name_ttl=name_ttl,
            pointers=pointers,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
            account_id=account_id,
            name_id=name_id,
            recipient_id=recipient_id,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
            account_id=account_id,
            name_id=name_id,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
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
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
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
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
            account_id=account_id,
            query_format=query_format,
            response_format=response_format,
            query_fee=query_fee,
            oracle_ttl=dict(
                type=ttl_type,
                value=ttl_value),
            vm_version=vm_version,
            fee=fee,
            ttl=ttl,
            nonce=nonce
        )
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
            sender_id=sender_id,
            oracle_id=oracle_id,
            response_ttl=dict(
                type=response_ttl_type,
                value=response_ttl_value
            ),
            query=query,
            query_ttl=dict(
                type=query_ttl_type,
                value=query_ttl_value
            ),
            fee=fee,
            query_fee=query_fee,
            ttl=ttl,
            nonce=nonce,
        )
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
            response_ttl=dict(
                type=response_ttl_type,
                value=response_ttl_value
            ),
            oracle_id=oracle_id,
            query_id=query_id,
            response=response,
            fee=fee,
            ttl=ttl,
            nonce=nonce,
        )
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
            oracle_id=oracle_id,
            oracle_ttl=dict(
                type=ttl_type,
                value=ttl_value
            ),
            fee=fee,
            ttl=ttl,
            nonce=nonce,
        )
        return _tx_native(op=PACK_TX, **body)
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
            vsn=idf.VSN,
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
        return _tx_native(op=PACK_TX, **body)

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
        tx = tx.tx if hasattr(tx, "tx") else tx
        body = dict(
            tag=idf.OBJECT_TAG_GA_META_TRANSACTION,
            vsn=idf.VSN,
            ga_id=ga_id,
            auth_data=auth_data,
            abi_version=abi_version,
            fee=fee,
            gas=gas,
            gas_price=gas_price,
            ttl=ttl,
            tx=tx,
        )
        return _tx_native(op=PACK_TX, **body)


class TxBuilderDebug:
    def __init__(self, api: OpenAPICli):
        """
        :param native: if the transactions should be built by the sdk (True) or requested to the debug api (False)
        """
        if api is None:
            raise ValueError("A initialized api rest client has to be provided to build a transaction using the node internal API ")
        self.api = api
