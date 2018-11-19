from aeternity import hashing
from aeternity.openapi import OpenAPICli
from aeternity.config import ORACLE_DEFAULT_TTL_TYPE_DELTA
import math

# RLP version number
# https://github.com/aeternity/protocol/blob/api-v0.10.1/serializations.md#binary-serialization
VSN = 1

# Tag constant for ids (type uint8)
# see https://github.com/aeternity/protocol/blob/master/serializations.md#the-id-type
# <<Tag:1/unsigned-integer-unit:8, Hash:32/binary-unit:8>>
ID_TAG_ACCOUNT = 1
ID_TAG_NAME = 2
ID_TAG_COMMITMENT = 3
ID_TAG_ORACLE = 4
ID_TAG_CONTRACT = 5
ID_TAG_CHANNEL = 6

# Object tags
# see https://github.com/aeternity/protocol/blob/master/serializations.md#binary-serialization

OBJECT_TAG_ACCOUNT = 10
OBJECT_TAG_SIGNED_TRANSACTION = 11
OBJECT_TAG_SPEND_TRANSACTION = 12
OBJECT_TAG_ORACLE = 20
OBJECT_TAG_ORACLE_QUERY = 21
OBJECT_TAG_ORACLE_REGISTER_TRANSACTION = 22
OBJECT_TAG_ORACLE_QUERY_TRANSACTION = 23
OBJECT_TAG_ORACLE_RESPONSE_TRANSACTION = 24
OBJECT_TAG_ORACLE_EXTEND_TRANSACTION = 25
OBJECT_TAG_NAME_SERVICE_NAME = 30
OBJECT_TAG_NAME_SERVICE_COMMITMENT = 31
OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION = 32
OBJECT_TAG_NAME_SERVICE_PRECLAIM_TRANSACTION = 33
OBJECT_TAG_NAME_SERVICE_UPDATE_TRANSACTION = 34
OBJECT_TAG_NAME_SERVICE_REVOKE_TRANSACTION = 35
OBJECT_TAG_NAME_SERVICE_TRANSFER_TRANSACTION = 36
OBJECT_TAG_CONTRACT = 40
OBJECT_TAG_CONTRACT_CALL = 41
OBJECT_TAG_CONTRACT_CREATE_TRANSACTION = 42
OBJECT_TAG_CONTRACT_CALL_TRANSACTION = 43
OBJECT_TAG_CHANNEL_CREATE_TRANSACTION = 50
OBJECT_TAG_CHANNEL_DEPOSIT_TRANSACTION = 51
OBJECT_TAG_CHANNEL_WITHDRAW_TRANSACTION = 52
OBJECT_TAG_CHANNEL_FORCE_PROGRESS_TRANSACTION = 521
OBJECT_TAG_CHANNEL_CLOSE_MUTUAL_TRANSACTION = 53
OBJECT_TAG_CHANNEL_CLOSE_SOLO_TRANSACTION = 54
OBJECT_TAG_CHANNEL_SLASH_TRANSACTION = 55
OBJECT_TAG_CHANNEL_SETTLE_TRANSACTION = 56
OBJECT_TAG_CHANNEL_OFF_CHAIN_TRANSACTION = 57
OBJECT_TAG_CHANNEL_OFF_CHAIN_UPDATE_TRANSFER = 570
OBJECT_TAG_CHANNEL_OFF_CHAIN_UPDATE_DEPOSIT = 571
OBJECT_TAG_CHANNEL_OFF_CHAIN_UPDATE_WITHDRAWAL = 572
OBJECT_TAG_CHANNEL_OFF_CHAIN_UPDATE_CREATE_CONTRACT = 573
OBJECT_TAG_CHANNEL_OFF_CHAIN_UPDATE_CALL_CONTRACT = 574
OBJECT_TAG_CHANNEL = 58
OBJECT_TAG_CHANNEL_SNAPSHOT_TRANSACTION = 59
OBJECT_TAG_POI = 60
OBJECT_TAG_MICRO_BODY = 101
OBJECT_TAG_LIGHT_MICRO_BLOCK = 102


def _int(val: int) -> bytes:
    s = int(math.ceil(val.bit_length() / 8))
    return val.to_bytes(s, 'big')


def _binary(val):
    """
    Encode a value to bytes.
    If the value is an int it will be encoded as bytes big endian
    Raises ValueError if the input is not an int or string
    """
    if isinstance(val, int) or isinstance(val, float):
        s = int(math.ceil(val.bit_length() / 8))
        return val.to_bytes(s, 'big')
    if isinstance(val, str):
        return val.encode("utf-8")
    if isinstance(val, bytes):
        return val
    raise ValueError("Byte serialization not supported")


def _id(id_tag, hash_id):
    """Utility function to create and _id type"""
    return _int(id_tag) + hashing.decode(hash_id)


class TxSigner:
    """
    TxSigner is used to sign transactions
    """

    def __init__(self, account, network_id):
        self.account = account
        self.network_id = network_id

    def encode_signed_transaction(self, transaction, signature):
        """prepare a signed transaction message"""
        tag = bytes([OBJECT_TAG_SIGNED_TRANSACTION])
        vsn = bytes([VSN])
        encoded_signed_tx = hashing.encode_rlp("tx", [tag, vsn, [signature], transaction])
        encoded_signature = hashing.encode("sg", signature)
        return encoded_signed_tx, encoded_signature

    def sign_encode_transaction(self, tx):
        """
        Sign, encode and compute the hash of a transaction
        :return: encoded_signed_tx, encoded_signature, tx_hash
        """
        # decode the transaction if not in native mode
        transaction = hashing.decode(tx.tx) if hasattr(tx, "tx") else hashing.decode(tx)
        # sign the transaction
        signature = self.account.sign(_binary(self.network_id) + transaction)
        # encode the transaction
        encoded_signed_tx, encoded_signature = self.encode_signed_transaction(transaction, signature)
        # compute the hash
        tx_hash = TxBuilder.compute_tx_hash(encoded_signed_tx)
        # return the
        return encoded_signed_tx, encoded_signature, tx_hash


class TxBuilder:
    """
    TxBuilder is used to build and post transactions to the chain.
    """

    def __init__(self, native=False, api: OpenAPICli =None):
        """
        :param native: if the transactions should be built by the sdk (True) or requested to the debug api (False)
        """
        if not native and api is None:
            raise ValueError("A initialized api rest client has to be provided to build a transaction using the node internal API ")
        self.api = api
        self.native_transactions = native

    @staticmethod
    def compute_tx_hash(signed_tx: str) -> str:
        """
        Generate the hash from a signed and encoded transaction
        :param signed_tx: an encoded signed transaction
        """
        signed = hashing.decode(signed_tx)
        return hashing.hash_encode("th", signed)

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
        # compute the absolute ttl and the nonce
        if self.native_transactions:
            tx = [
                _int(OBJECT_TAG_SPEND_TRANSACTION),
                _int(VSN),
                _id(ID_TAG_ACCOUNT, account_id),
                _id(ID_TAG_ACCOUNT, recipient_id),
                _int(amount),
                _int(fee),
                _int(ttl),
                _int(nonce),
                _binary(payload)
            ]
            tx = hashing.encode_rlp("tx", tx)
            return tx

        # use internal endpoints transaction
        body = {
            "recipient_id": recipient_id,
            "amount": amount,
            "fee":  fee,
            "sender_id": account_id,
            "payload": payload,
            "ttl": ttl,
            "nonce": nonce,
        }
        return self.api.post_spend(body=body).tx

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
        if self.native_transactions:
            tx = [
                _int(OBJECT_TAG_NAME_SERVICE_PRECLAIM_TRANSACTION),
                _int(VSN),
                _id(ID_TAG_ACCOUNT, account_id),
                _int(nonce),
                _id(ID_TAG_COMMITMENT, commitment_id),
                _int(fee),
                _int(ttl)
            ]
            return hashing.encode_rlp("tx", tx)
        # use internal endpoints transaction
        body = dict(
            commitment_id=commitment_id,
            fee=fee,
            account_id=account_id,
            ttl=ttl,
            nonce=nonce
        )
        return self.api.post_name_preclaim(body=body).tx

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
        if self.native_transactions:
            tx = [
                _int(OBJECT_TAG_NAME_SERVICE_CLAIM_TRANSACTION),
                _int(VSN),
                _id(ID_TAG_ACCOUNT, account_id),
                _int(nonce),
                hashing.decode(name),
                _binary(name_salt),
                _int(fee),
                _int(ttl)
            ]
            tx = hashing.encode_rlp("tx", tx)
        # use internal endpoints transaction
        body = dict(
            account_id=account_id,
            name=name,
            name_salt=name_salt,
            fee=fee,
            ttl=ttl,
            nonce=nonce
        )
        return self.api.post_name_claim(body=body).tx

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
        if self.native_transactions:
            # TODO: verify supported keys for name updates
            def pointer_tag(pointer):
                return {
                    "account_pubkey": ID_TAG_ACCOUNT,
                    "oracle_pubkey": ID_TAG_ORACLE,
                    "contract_pubkey": ID_TAG_CONTRACT,
                    "channel_pubkey": ID_TAG_CHANNEL
                }.get(pointer.get("key"))
            ptrs = [[_binary(p.get("key")), _id(pointer_tag(p), p.get("id"))] for p in pointers]
            # build tx
            tx = [
                _int(OBJECT_TAG_NAME_SERVICE_UPDATE_TRANSACTION),
                _int(VSN),
                _id(ID_TAG_ACCOUNT, account_id),
                _int(nonce),
                _id(ID_TAG_NAME, name_id),
                _int(name_ttl),
                ptrs,
                _int(client_ttl),
                _int(fee),
                _int(ttl)
            ]
            return hashing.encode_rlp("tx", tx)
        # use internal endpoints transaction
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
        return self.api.post_name_update(body=body).tx

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
        if self.native_transactions:
            tx = [
                _int(OBJECT_TAG_NAME_SERVICE_TRANSFER_TRANSACTION),
                _int(VSN),
                _id(ID_TAG_ACCOUNT, account_id),
                _int(nonce),
                _id(ID_TAG_NAME, name_id),
                _id(ID_TAG_ACCOUNT, recipient_id),
                _int(fee),
                _int(ttl),
            ]
            return hashing.encode_rlp("tx", tx)
        # use internal endpoints transaction
        body = dict(
            account_id=account_id,
            name_id=name_id,
            recipient_id=recipient_id,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        return self.api.post_name_transfer(body=body).tx

    def tx_name_revoke(self, account_id, name_id, fee, ttl, nonce)-> str:
        """
        create a revoke transaction
        :param account_id: the account revoking the name
        :param name_id: the name to revoke
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        :param nonce: the nonce of the account for the transaction
        """

        if self.native_transactions:
            tx = [
                _int(OBJECT_TAG_NAME_SERVICE_REVOKE_TRANSACTION),
                _int(VSN),
                _id(ID_TAG_ACCOUNT, account_id),
                _int(nonce),
                _id(ID_TAG_NAME, name_id),
                _int(fee),
                _int(ttl),
            ]
            return hashing.encode_rlp("tx", tx)
        # use internal endpoints transaction
        body = dict(
            account_id=account_id,
            name_id=name_id,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        return self.api.post_name_revoke(body=body).tx

    # CONTRACTS

    def tx_contract_create(self, account_id, code, call_data, amount, deposit, gas, gas_price, vm_version, fee, ttl, nonce)-> str:
        """
        Create a contract transaction
        :param account_id: the account creating the contract
        :param code: the binary code of the contract
        :param call_data: the call data for the contract
        :param amount: TODO: add definition
        :param deposit: TODO: add definition
        :param gas: TODO: add definition
        :param gas_price: TODO: add definition
        :param vm_version: TODO: add definition
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        :param nonce: the nonce of the account for the transaction
        """

        if self.native_transactions:
            raise NotImplementedError("Native transaction for contract creation not implemented")
        # use internal endpoints transaction
        body = dict(
            owner_id=account_id,
            amount=amount,
            deposit=deposit,
            fee=fee,
            gas=gas,
            gas_price=gas_price,
            vm_version=vm_version,
            call_data=call_data,
            code=code,
            ttl=ttl,
            nonce=nonce
        )
        tx = self.api.post_contract_create(body=body)
        return tx.tx, tx.contract_id

    def tx_contract_call(self, account_id, contract_id, call_data, function, arg, amount, gas, gas_price, vm_version, fee, ttl, nonce)-> str:
        # compute the absolute ttl and the nonce
        if self.native_transactions:
            raise NotImplementedError("Native transaction for contract calls not implemented")
        # use internal endpoints transaction
        body = dict(
            call_data=call_data,
            caller_id=account_id,
            contract_id=contract_id,
            amount=amount,
            fee=fee,
            gas=gas,
            gas_price=gas_price,
            vm_version=vm_version,
            ttl=ttl,
            nonce=nonce
        )
        return self.api.post_contract_call(body=body).tx

    # ORACLES

    def tx_oracle_register(self, account_id, query_format, response_format, query_fee, ttl_type, ttl_value, vm_version, fee, ttl, nonce)-> str:
        """
        Create an register oracle transaction
        """

        if self.native_transactions:
            tx = [
                _int(OBJECT_TAG_ORACLE_REGISTER_TRANSACTION),
                _int(VSN),
                _id(ID_TAG_ACCOUNT, account_id),
                _int(nonce),
                _binary(query_format),
                _binary(response_format),
                _int(query_fee),
                _int(0 if ttl_type == ORACLE_DEFAULT_TTL_TYPE_DELTA else 2),
                _int(ttl_value),
                _int(fee),
                _int(ttl),
            ]
            return hashing.encode_rlp("tx", tx)
        # use internal endpoints transaction
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
        tx = self.api.post_oracle_register(body=body)
        return tx.tx
