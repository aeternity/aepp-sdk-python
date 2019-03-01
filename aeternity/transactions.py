from aeternity.hashing import _int, _int_decode, _binary, _id, encode, decode, encode_rlp, decode_rlp, hash_encode, contract_id
from aeternity.openapi import OpenAPICli
from aeternity.config import ORACLE_DEFAULT_TTL_TYPE_DELTA
from aeternity import identifiers as idf
from aeternity.exceptions import UnsupportedTransactionType
import rlp
import math
import namedtupled

BASE_GAS = 15000
GAS_PER_BYTE = 20
GAS_PRICE = 1000000000
KEY_BLOCK_INTERVAL = 3


class TxSigner:
    """
    TxSigner is used to sign transactions
    """

    def __init__(self, account, network_id):
        self.account = account
        self.network_id = network_id

    def encode_signed_transaction(self, transaction, signature):
        """prepare a signed transaction message"""
        tag = bytes([idf.OBJECT_TAG_SIGNED_TRANSACTION])
        vsn = bytes([idf.VSN])
        encoded_signed_tx = encode_rlp(idf.TRANSACTION, [tag, vsn, [signature], transaction])
        encoded_signature = encode(idf.SIGNATURE, signature)
        return encoded_signed_tx, encoded_signature

    def sign_encode_transaction(self, tx):
        """
        Sign, encode and compute the hash of a transaction
        :return: encoded_signed_tx, encoded_signature, tx_hash
        """
        # decode the transaction if not in native mode
        transaction = _tx_native(op=UNPACK_TX, tx=tx.tx if hasattr(tx, "tx") else tx)
        # get the transaction as byte list
        tx_raw = decode(transaction.tx)
        # sign the transaction
        signature = self.account.sign(_binary(self.network_id) + tx_raw)
        # encode the transaction
        encoded_signed_tx, encoded_signature = self.encode_signed_transaction(tx_raw, signature)
        # compute the hash
        tx_hash = TxBuilder.compute_tx_hash(encoded_signed_tx)
        # return the object
        tx = dict(
          data=transaction.data,
          tx=encoded_signed_tx,
          hash=tx_hash,
          signature=encoded_signature,
          network_id=self.network_id,
        )
        return namedtupled.map(tx, _nt_name="TxObject")


class TxObject:
    def __init__(self, tx_data, tx, hash):
        self.data = tx_data
        self.tx = tx
        self.hash = hash
        self._as_bytes = decode(self.tx)

    def set_properties(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


PACK_TX = 1
UNPACK_TX = 0


def _tx_native(op, **kwargs):

    def std_fee(tx_raw, fee_idx, base_gas_multiplier=1):
        # calculates the standard minimum transaction fee
        tx_copy = tx_raw  # create a copy of the input
        tx_copy[fee_idx] = _int(0, 8)
        return (BASE_GAS * base_gas_multiplier + len(rlp.encode(tx_copy)) * GAS_PER_BYTE) * GAS_PRICE

    def contract_fee(tx_raw, fee_idx, gas, base_gas_multiplier=1):
        # estimate the contract creation fee
        tx_copy = tx_raw  # create a copy of the input
        tx_copy[fee_idx] = _int(0, 8)
        return (BASE_GAS * base_gas_multiplier + gas + len(rlp.encode(tx_copy)) * GAS_PER_BYTE) * GAS_PRICE

    def oracle_fee(tx_raw, fee_idx, relative_ttl):
        tx_copy = tx_raw  # create a copy of the input
        tx_copy[fee_idx] = _int(0, 8)
        fee = (BASE_GAS + len(rlp.encode(tx_copy)) * GAS_PER_BYTE)
        fee += math.ceil(32000 * relative_ttl / math.floor(60 * 24 * 365 / KEY_BLOCK_INTERVAL))
        return fee * GAS_PRICE

    def build_tx_object(tx_data, tx_raw, fee_idx, min_fee):
        if tx_data.get("fee") < min_fee:
            tx_native[fee_idx] = _int(min_fee)
            tx_data["fee"] = min_fee
        tx_encoded = encode_rlp(idf.TRANSACTION, tx_native)
        tx = dict(
            data=tx_data,
            tx=tx_encoded,
            hash=TxBuilder.compute_tx_hash(tx_encoded),
        )
        return namedtupled.map(tx, _nt_name="TxObject")

    if op == PACK_TX:
        tag = kwargs.get("tag", 0)
        vsn = kwargs.get("vsn", 1)
    else:
        tx_native = decode_rlp(kwargs.get("tx", []))
        tag = int.from_bytes(tx_native[0], "big")

    if tag == idf.OBJECT_TAG_SPEND_TRANSACTION:
        tx = {}
        tx_field_fee_index = 5
        if op == PACK_TX:  # pack transaction
            tx_native = [
                _int(tag),
                _int(vsn),
                _id(idf.ID_TAG_ACCOUNT, kwargs.get("sender_id")),
                _id(idf.ID_TAG_ACCOUNT, kwargs.get("recipient_id")),
                _int(kwargs.get("amount")),
                _int(kwargs.get("fee")),  # index 5
                _int(kwargs.get("ttl")),
                _int(kwargs.get("nonce")),
                _binary(kwargs.get("payload"))
            ]
            min_fee = std_fee(tx_native, tx_field_fee_index)
            tx = build_tx_object(kwargs, tx_native, tx_field_fee_index, min_fee)
        else:  # unpack transaction
            tx_native = decode_rlp(kwargs.get("tx"))
            tx_data = dict(
                tag=tag,
                vsn=_int_decode(tx_native[1]),
                sender_id=encode(idf.ACCOUNT_ID, tx_native[2]),
                recipient_id=encode(idf.ACCOUNT_ID, tx_native[3]),
                amount=_int_decode(tx_native[4]),
                fee=_int_decode(tx_native[5]),
                ttl=_int_decode(tx_native[6]),
                nonce=_int_decode(tx_native[7]),
                payload=tx_native[8].hex(),
            )
            tx = build_tx_object(tx_data, tx_native, tx_field_fee_index, tx_data.get("fee"))
        return tx
    elif tag == idf.OBJECT_TAG_NAME_SERVICE_PRECLAIM_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("account_id")),
            _int(kwargs.get("nonce")),
            _id(idf.ID_TAG_COMMITMENT, kwargs.get("commitment_id")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("ttl"))
        ]
        tx_field_fee_index = 5
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("account_id")),
            _int(kwargs.get("nonce")),
            decode(kwargs.get("name")),
            _binary(kwargs.get("name_salt")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("ttl"))
        ]
        tx_field_fee_index = 6
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_NAME_SERVICE_UPDATE_TRANSACTION:
        # first asseble the pointers
        def pointer_tag(pointer):
            return {
                "account_pubkey": idf.ID_TAG_ACCOUNT,
                "oracle_pubkey": idf.ID_TAG_ORACLE,
                "contract_pubkey": idf.ID_TAG_CONTRACT,
                "channel_pubkey": idf.ID_TAG_CHANNEL
            }.get(pointer.get("key"))
        ptrs = [[_binary(p.get("key")), _id(pointer_tag(p), p.get("id"))] for p in kwargs.get("pointers", [])]
        # then build the transaction
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("account_id")),
            _int(kwargs.get("nonce")),
            _id(idf.ID_TAG_NAME, kwargs.get("name_id")),
            _int(kwargs.get("name_ttl")),
            ptrs,
            _int(kwargs.get("client_ttl")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("ttl"))
        ]
        tx_field_fee_index = 8
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_NAME_SERVICE_TRANSFER_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("account_id")),
            _int(kwargs.get("nonce")),
            _id(idf.ID_TAG_NAME, kwargs.get("name_id")),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("recipient_id")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("ttl")),
        ]
        tx_field_fee_index = 6
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_NAME_SERVICE_REVOKE_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("account_id")),
            _int(kwargs.get("nonce")),
            _id(idf.ID_TAG_NAME, kwargs.get("name_id")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("ttl")),
        ]
        tx_field_fee_index = 5
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_CONTRACT_CREATE_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("owner_id")),
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
        tx_field_fee_index = 6
        # TODO: verify the fee caluclation for the contract
        min_fee = contract_fee(tx_native, tx_field_fee_index, kwargs.get("gas"),  base_gas_multiplier=5)
    elif tag == idf.OBJECT_TAG_CONTRACT_CALL_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("caller_id")),
            _int(kwargs.get("nonce")),
            _id(idf.ID_TAG_CONTRACT, kwargs.get("contract_id")),
            _int(kwargs.get("abi_version")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("ttl")),
            _int(kwargs.get("amount")),
            _int(kwargs.get("gas")),
            _int(kwargs.get("gas_price")),
            _binary(decode(kwargs.get("call_data"))),
        ]
        tx_field_fee_index = 6
        min_fee = contract_fee(tx_native, tx_field_fee_index, kwargs.get("gas"),  base_gas_multiplier=30)
    elif tag == idf.OBJECT_TAG_CHANNEL_CREATE_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("initiator")),
            _int(kwargs.get("initiator_amount")),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("responder")),
            _int(kwargs.get("responder_amount")),
            _int(kwargs.get("channel_reserve")),
            _int(kwargs.get("lock_period")),
            _int(kwargs.get("ttl")),
            _int(kwargs.get("fee")),
            # _[id(delegate_ids)], TODO: handle delegate ids
            _binary(kwargs.get("state_hash")),
            _int(kwargs.get("nonce")),
        ]
        tx_field_fee_index = 9
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_CHANNEL_DEPOSIT_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_CHANNEL, kwargs.get("channel_id")),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("from_id")),
            _int(kwargs.get("amount")),
            _int(kwargs.get("ttl")),
            _int(kwargs.get("fee")),
            _binary(kwargs.get("state_hash")),
            _int(kwargs.get("round")),
            _int(kwargs.get("nonce")),
        ]
        tx_field_fee_index = 6
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_CHANNEL_WITHDRAW_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_CHANNEL, kwargs.get("channel_id")),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("to_id")),
            _int(kwargs.get("amount")),
            _int(kwargs.get("ttl")),
            _int(kwargs.get("fee")),
            _binary(kwargs.get("state_hash")),
            _int(kwargs.get("round")),
            _int(kwargs.get("nonce")),
        ]
        tx_field_fee_index = 6
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_CHANNEL_CLOSE_MUTUAL_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_CHANNEL, kwargs.get("channel_id")),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("from_id")),
            _int(kwargs.get("initiator_amount_final")),
            _int(kwargs.get("responder_amount_final")),
            _int(kwargs.get("ttl")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("nonce")),
        ]
        tx_field_fee_index = 7
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_CHANNEL_CLOSE_SOLO_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_CHANNEL, kwargs.get("channel_id")),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("from_id")),
            _binary(kwargs.get("payload")),
            # _poi(kwargs.get("poi")), TODO: implement support for _poi
            _int(kwargs.get("ttl")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("nonce")),
        ]
        tx_field_fee_index = 7
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_CHANNEL_SLASH_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_CHANNEL, kwargs.get("channel_id")),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("from_id")),
            _binary(kwargs.get("payload")),
            # _poi(kwargs.get("poi")), TODO: implement support for _poi
            _int(kwargs.get("ttl")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("nonce")),
        ]
        tx_field_fee_index = 7
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_CHANNEL_SETTLE_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_CHANNEL, kwargs.get("channel_id")),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("from_id")),
            _int(kwargs.get("initiator_amount_final")),
            _int(kwargs.get("responder_amount_final")),
            _int(kwargs.get("ttl")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("nonce")),
        ]
        tx_field_fee_index = 7
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_CHANNEL_SNAPSHOT_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_CHANNEL, kwargs.get("channel_id")),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("from_id")),
            _binary(kwargs.get("payload")),
            _int(kwargs.get("ttl")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("nonce")),
        ]
        tx_field_fee_index = 6
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_CHANNEL_FORCE_PROGRESS_TRANSACTION:
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_CHANNEL, kwargs.get("channel_id")),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("from_id")),
            _binary(kwargs.get("payload")),
            _int(kwargs.get("round")),
            _binary(kwargs.get("update")),
            _binary(kwargs.get("state_hash")),
            # _trees(kwargs.get("offchain_trees")), TODO: implement support for _trees
            _int(kwargs.get("ttl")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("nonce")),
        ]
        tx_field_fee_index = 9
        min_fee = std_fee(tx_native, tx_field_fee_index)
    elif tag == idf.OBJECT_TAG_ORACLE_REGISTER_TRANSACTION:
        oracle_ttl = kwargs.get("oracle_ttl", {})
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("account_id")),
            _int(kwargs.get("nonce")),
            _binary(kwargs.get("query_format")),
            _binary(kwargs.get("response_format")),
            _int(kwargs.get("query_fee")),
            _int(0 if oracle_ttl.get("type") == ORACLE_DEFAULT_TTL_TYPE_DELTA else 1),
            _int(oracle_ttl.get("value")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("ttl")),
            _int(kwargs.get("vm_version")),
        ]
        tx_field_fee_index = 9
        min_fee = oracle_fee(tx_native, tx_field_fee_index, oracle_ttl.get("value"))
    elif tag == idf.OBJECT_TAG_ORACLE_QUERY_TRANSACTION:
        query_ttl = kwargs.get("query_ttl", {})
        response_ttl = kwargs.get("response_ttl", {})
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ACCOUNT, kwargs.get("sender_id")),
            _int(kwargs.get("nonce")),
            _id(idf.ID_TAG_ORACLE, kwargs.get("oracle_id")),
            _binary(kwargs.get("query")),
            _int(kwargs.get("query_fee")),
            _int(0 if query_ttl.get("type") == ORACLE_DEFAULT_TTL_TYPE_DELTA else 1),
            _int(query_ttl.get("value")),
            _int(0 if response_ttl.get("type") == ORACLE_DEFAULT_TTL_TYPE_DELTA else 1),
            _int(response_ttl.get("value")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("ttl")),
        ]
        tx_field_fee_index = 11
        min_fee = oracle_fee(tx_native, tx_field_fee_index, query_ttl.get("value"))
    elif tag == idf.OBJECT_TAG_ORACLE_RESPONSE_TRANSACTION:
        response_ttl = kwargs.get("response_ttl", {})
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ORACLE, kwargs.get("oracle_id")),
            _int(kwargs.get("nonce")),
            decode(kwargs.get("query_id")),
            _binary(kwargs.get("response")),
            _int(0 if response_ttl.get("type") == ORACLE_DEFAULT_TTL_TYPE_DELTA else 1),
            _int(response_ttl.get("value")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("ttl")),
        ]
        tx_field_fee_index = 8
        min_fee = oracle_fee(tx_native, tx_field_fee_index, response_ttl.get("value"))
    elif tag == idf.OBJECT_TAG_ORACLE_EXTEND_TRANSACTION:
        oracle_ttl = kwargs.get("oracle_ttl", {})
        tx_native = [
            _int(tag),
            _int(vsn),
            _id(idf.ID_TAG_ORACLE, kwargs.get("oracle_id")),
            _int(kwargs.get("nonce")),
            _int(0 if oracle_ttl.get("type", {}) == ORACLE_DEFAULT_TTL_TYPE_DELTA else 1),
            _int(oracle_ttl.get("value")),
            _int(kwargs.get("fee")),
            _int(kwargs.get("ttl")),
        ]
        tx_field_fee_index = 6
        min_fee = oracle_fee(tx_native, tx_field_fee_index, oracle_ttl.get("value"))
    else:
        raise UnsupportedTransactionType(f"Unusupported transaction tag {tag}")


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

    def tx_spend(self, account_id, recipient_id, amount, payload, fee, ttl, nonce)-> str:
        """
        create a spend transaction
        :param account_id: the public key of the sender
        :param recipient_id: the public key of the recipient
        :param amount: the amount to send
        :param payload: the payload associated with the data
        :param fee: the fee for the transaction
        :param ttl: the absolute ttl of the transaction
        :param nonce: the nonce of the transaction
        """
        # use internal endpoints transaction
        body = {
            "tag": idf.OBJECT_TAG_SPEND_TRANSACTION,
            "vsn": idf.VSN,
            "recipient_id": recipient_id,
            "amount": amount,
            "fee":  fee,
            "sender_id": account_id,
            "payload": payload,
            "ttl": ttl,
            "nonce": nonce,
        }
        return _tx_native(op=PACK_TX, **body)
        # return self.api.post_spend(body=body).tx

    # NAMING #

    def tx_name_preclaim(self, account_id, commitment_id, fee, ttl, nonce)-> str:
        """
        create a preclaim transaction
        :param account_id: the account registering the name
        :param commitment_id: the commitment id
        :param fee:  the fee for the transaction
        :param ttl:  the ttl for the transaction
        :param nonce: the nonce of the account for the transaction
        """
        body = dict(
            commitment_id=commitment_id,
            fee=fee,
            account_id=account_id,
            ttl=ttl,
            nonce=nonce
        )
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_NAME_SERVICE_PRECLAIM_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native
        # sreturn self.api.post_name_preclaim(body=body).tx

    def tx_name_claim(self, account_id, name, name_salt, fee, ttl, nonce)-> str:
        """
        create a preclaim transaction
        :param account_id: the account registering the name
        :param commitment_id: the commitment id
        :param commitment_hash:  the commitment hash
        :param fee:  the fee for the transaction
        :param ttl:  the ttl for the transaction
        :param nonce: the nonce of the account for the transaction
        """
        body = dict(
            account_id=account_id,
            name=name,
            name_salt=name_salt,
            fee=fee,
            ttl=ttl,
            nonce=nonce
        )
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native
        # return self.api.post_name_claim(body=body).tx

    def tx_name_update(self, account_id, name_id, pointers, name_ttl, client_ttl, fee, ttl, nonce)-> str:
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
            account_id=account_id,
            name_id=name_id,
            client_ttl=client_ttl,
            name_ttl=name_ttl,
            pointers=pointers,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_NAME_SERVICE_UPDATE_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native
        # return self.api.post_name_update(body=body).tx

    def tx_name_transfer(self, account_id, name_id, recipient_id, fee, ttl, nonce)-> str:
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
            account_id=account_id,
            name_id=name_id,
            recipient_id=recipient_id,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_NAME_SERVICE_TRANSFER_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native
        # return self.api.post_name_transfer(body=body).tx

    def tx_name_revoke(self, account_id, name_id, fee, ttl, nonce)-> str:
        """
        create a revoke transaction
        :param account_id: the account revoking the name
        :param name_id: the name to revoke
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        :param nonce: the nonce of the account for the transaction
        """

        body = dict(
            account_id=account_id,
            name_id=name_id,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_NAME_SERVICE_REVOKE_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native
        # return self.api.post_name_revoke(body=body).tx

    # CONTRACTS

    def tx_contract_create(self, owner_id, code, call_data, amount, deposit, gas, gas_price, vm_version, abi_version, fee, ttl, nonce)-> str:
        """
        Create a contract transaction
        :param owner_id: the account creating the contract
        :param code: the binary code of the contract
        :param call_data: the call data for the contract
        :param amount: TODO: add definition
        :param deposit: TODO: add definition
        :param gas: TODO: add definition
        :param gas_price: TODO: add definition
        :param vm_version: TODO: add definition
        :param abi_version: TODO: add definition
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        :param nonce: the nonce of the account for the transaction
        """
        body = dict(
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
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_CONTRACT_CREATE_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native, contract_id(owner_id, nonce)
        # tx = self.api.post_contract_create(body=body)
        # return tx.tx, tx.contract_id

    def tx_contract_call(self, caller_id, contract_id, call_data, function, arg, amount, gas, gas_price, abi_version, fee, ttl, nonce)-> str:
        """
        Create a contract call
        :param caller_id: the account creating the contract
        :param contract_id: the contract to call
        :param call_data: the call data for the contract
        :param function: the function to execute
        :param arg: the function arguments
        :param amount: TODO: add definition
        :param gas: TODO: add definition
        :param gas_price: TODO: add definition
        :param vm_version: TODO: add definition
        :param abi_version: TODO: add definition
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        :param nonce: the nonce of the account for the transaction
        """

        body = dict(
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
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_CONTRACT_CALL_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native
        # return self.api.post_contract_call(body=body).tx

    # ORACLES

    def tx_oracle_register(self, account_id,
                           query_format, response_format,
                           query_fee, ttl_type, ttl_value, vm_version,
                           fee, ttl, nonce)-> str:
        """
        Create a register oracle transaction
        """
        body = dict(
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
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_ORACLE_REGISTER_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native
        # tx = self.api.post_oracle_register(body=body)
        # return tx.tx

    def tx_oracle_query(self, oracle_id, sender_id, query,
                        query_fee, query_ttl_type, query_ttl_value,
                        response_ttl_type, response_ttl_value,
                        fee, ttl, nonce)-> str:
        """
        Create a oracle query transaction
        """

        body = dict(
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
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_ORACLE_QUERY_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native
        # tx = self.api.post_oracle_query(body=body)
        # return tx.tx

    def tx_oracle_respond(self, oracle_id, query_id, response,
                          response_ttl_type, response_ttl_value,
                          fee, ttl, nonce)-> str:
        """
        Create a oracle response transaction
        """
        body = dict(
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
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_ORACLE_RESPONSE_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native
        # tx = self.api.post_oracle_respond(body=body)
        # return tx.tx

    def tx_oracle_extend(self, oracle_id,
                         ttl_type, ttl_value,
                         fee, ttl, nonce)-> str:
        """
        Create a oracle extends transaction
        """
        body = dict(
            oracle_id=oracle_id,
            oracle_ttl=dict(
                type=ttl_type,
                value=ttl_value
            ),
            fee=fee,
            ttl=ttl,
            nonce=nonce,
        )
        tx_native, min_fee = _tx_native(idf.OBJECT_TAG_ORACLE_EXTEND_TRANSACTION, idf.VSN, **body)
        # compute the absolute ttl and the nonce
        return tx_native
        # tx = self.api.post_oracle_extend(body=body)
        # return tx.tx


class TxBuilderDebug:
    def __init__(self, api: OpenAPICli):
        """
        :param native: if the transactions should be built by the sdk (True) or requested to the debug api (False)
        """
        if api is None:
            raise ValueError("A initialized api rest client has to be provided to build a transaction using the node internal API ")
        self.api = api
