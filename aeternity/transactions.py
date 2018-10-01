from aeternity import hashing, config
from aeternity.openapi import OpenAPIClientException
from aeternity.exceptions import TransactionHashMismatch
import time
import random

# RLP version number
# https://github.com/aeternity/protocol/blob/epoch-v0.10.1/serializations.md#binary-serialization
VSN = 1

# The list of tags can be found here:
# https://github.com/aeternity/protocol/blob/epoch-v0.10.1/serializations.md#table-of-object-tags
TAG_SIGNED_TX = 11
TAG_SPEND_TX = 12


class TxNotIncluded(Exception):
    def __init__(self, tx_hash, reason):
        self.tx_hash = tx_hash
        self.reason = reason


class TxBuilder:
    """
    TxBuilder is used to build and post transactions to the chain.
    """

    def __init__(self, epoch, account):
        """
        :param epoch: the epoch rest client
        :param account: the account that will be signing the transactions
        """
        self.epoch = epoch
        self.account = account

    @staticmethod
    def compute_absolute_ttl(epoch, relative_ttl):
        """
        Compute the absolute ttl by adding the ttl to the current height of the chain
        :param epoch: the epoch client
        :param relative_ttl: the relative ttl, must be > 0
        """
        if relative_ttl <= 0:
            raise ValueError("ttl must be greather than 0")
        height = epoch.get_current_key_block_height()
        return height + relative_ttl

    @staticmethod
    def get_next_nonce(epoch, account_address):
        """
        Get the next nonce to be used for a transaction for an account
        :param epoch: the epoch client
        :return: the next nonce for an account
        """
        account = epoch.get_account_by_pubkey(pubkey=account_address)
        return account.nonce + 1

    @staticmethod
    def compute_tx_hash(signed_tx):
        """
        Generate the hash from a signed and encoded transaction
        :param signed_tx: an encoded signed transaction
        """
        signed = hashing.decode(signed_tx)
        return hashing.hash_encode("th", signed)

    def _get_nonce_ttl(self, relative_ttl):
        """
        Helper method to compute both ttl and nonce for a s
        """
        ttl = TxBuilder.compute_absolute_ttl(self.epoch, relative_ttl)
        nonce = TxBuilder.get_next_nonce(self.epoch, self.account.get_address())
        return nonce, ttl

    def encode_signed_transaction(self, signed_tx, signature):
        """prepare a signed transaction message"""
        tag = bytes([TAG_SIGNED_TX])
        vsn = bytes([VSN])
        encoded_signed_tx = hashing.encode_rlp("tx", [tag, vsn, [signature], signed_tx])
        encoded_signature = hashing.encode("sg", signature)
        return encoded_signed_tx, encoded_signature

    def sign_encode_transaction(self, tx):
        """
        sign, encode and compute the hash of a transaction
        """
        transaction = hashing.decode(tx.tx)
        # sign the transaction
        signature = self.account.sign(transaction)
        # encode the transaction
        encoded_signed_tx, encoded_signature = self.encode_signed_transaction(transaction, signature)
        # compute the hash
        tx_hash = TxBuilder.compute_tx_hash(encoded_signed_tx)
        # return the
        return encoded_signed_tx, encoded_signature, tx_hash

    def wait_tx(self, tx_hash, max_retries=config.MAX_RETRIES, polling_interval=config.POLLING_INTERVAL):
        """
        Wait for a transaction to be mined for an account
        this listen to pending transactions.
        The method will wait for a specific transaction to be included in the chain,
        it will return False if one of the following conditions are met:
        - the chain reply with a 404 not found (the transaction was expugned)
        - the account nonce is >= of the transaction nonce (transaction is in an illegal state)
        - the ttl of the transaction or the one passed as parameter has been reached
        :return: True if the transaction id found False otherwise
        """
        if max_retries <= 0:
            raise ValueError("Retries must be greather than 0")

        n = 1
        total_sleep = 0
        while True:
            # query the transaction
            try:
                tx = self.epoch.get_transaction_by_hash(hash=tx_hash)
                # get the account nonce
            except OpenAPIClientException as e:
                # it may fail because it is not found that means that
                # or it was invalid or the ttl has expired
                raise TxNotIncluded(tx_hash=tx_hash, reason=e.reason)
            # if the tx.block_height > 0 we win
            if tx.block_height > 0:
                break
            # get the transaction nonce
            tx_nonce = tx.tx.get('nonce')
            account_nonce = self.epoch.get_account_by_pubkey(pubkey=self.account.get_address()).nonce
            if account_nonce >= tx_nonce:
                # there is a possibility that a tx gets included
                # between the get_tx call and here, giving false negative
                # therefore we need to test the tx again before leaving
                tx = self.epoch.get_transaction_by_hash(hash=tx_hash)
                if tx.block_height <= 0:
                    raise TxNotIncluded(tx_hash=tx_hash, reason=f"The nonce for this transaction ({tx_nonce}) has been used ")

            if n >= max_retries:
                raise TxNotIncluded(tx_hash=tx_hash, reason=f"The transaction was not incluced in {total_sleep} seconds, wait aborted")
            # calculate sleep time
            sleep_time = (polling_interval ** n) + (random.randint(0, 1000) / 1000.0)
            time.sleep(sleep_time)
            total_sleep += sleep_time
            # increment n
            n += 1

    def post_transaction(self, tx, tx_hash):
        """
        post a transaction to the chain
        :return: the signed_transaction
        """
        reply = self.epoch.post_transaction(body={"tx": tx})
        if reply.tx_hash != tx_hash:
            raise TransactionHashMismatch(f"Transaction hash doesn't match, expected {tx_hash} got {reply.tx_hash}")

    def tx_spend(self, recipient_id, amount, payload, fee, ttl):
        """
        create a spend transaction
        :param recipient_id: the public key of the recipient
        :param amount: the amount to send
        :param payload: the payload associated with the data
        :param fee: the fee for the transaction
        :param ttl: the relative ttl of the transaction
        """
        # compute the absolute ttl and the nonce
        nonce, ttl = self._get_nonce_ttl(ttl)
        # send the update transaction
        body = {
            "recipient_id": recipient_id,
            "amount": amount,
            "fee":  fee,
            "sender_id": self.account.get_address(),
            "payload": payload,
            "ttl": ttl,
            "nonce": nonce,
        }
        # request a spend transaction
        # TODO: this should be computed locally
        tx = self.epoch.post_spend(body=body)
        return self.sign_encode_transaction(tx)

    # NAMING #

    def tx_name_preclaim(self, commitment_id, fee, ttl):
        """
        create a preclaim transaction
        :param commitment_id: the commitment id
        :param commitment_hash:  the commitment hash
        :param fee:  the fee for the transaction
        :param ttl:  the ttl for the transaction
        """
        nonce, ttl = self._get_nonce_ttl(ttl)
        body = dict(
            commitment_id=commitment_id,
            fee=fee,
            account_id=self.account.get_address(),
            ttl=ttl,
            nonce=nonce
        )
        tx = self.epoch.post_name_preclaim(body=body)
        return self.sign_encode_transaction(tx)

    def tx_name_claim(self, name, name_salt, fee, ttl):
        """
        create a preclaim transaction
        :param commitment_id: the commitment id
        :param commitment_hash:  the commitment hash
        :param fee:  the fee for the transaction
        :param ttl:  the ttl for the transaction
        """
        nonce, ttl = self._get_nonce_ttl(ttl)
        body = dict(
            account_id=self.account.get_address(),
            name=name,
            name_salt=name_salt,
            fee=fee,
            ttl=ttl,
            nonce=nonce
        )
        tx = self.epoch.post_name_claim(body=body)
        return self.sign_encode_transaction(tx)

    def tx_name_update(self, name_id, pointers, name_ttl, client_ttl, fee, ttl):
        """
        create an update transaction
        :param name_id: the name id
        :param pointers:  the pointers to update to
        :param name_ttl:  the ttl for the name registration
        :param client_ttl:  the ttl for client to cache the name
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        """
        nonce, ttl = self._get_nonce_ttl(ttl)
        body = dict(
            account_id=self.account.get_address(),
            name_id=name_id,
            client_ttl=client_ttl,
            name_ttl=name_ttl,
            pointers=pointers,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        tx = self.epoch.post_name_update(body=body)
        return self.sign_encode_transaction(tx)

    def tx_name_transfer(self, name_id, recipient_id, fee, ttl):
        """
        create a transfer transaction
        :param name_id: the name to transfer
        :param recipient_id: the address of the account to transfer the name to
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        """
        nonce, ttl = self._get_nonce_ttl(ttl)
        body = dict(
            account_id=self.account.get_address(),
            name_id=name_id,
            recipient_id=recipient_id,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        tx = self.epoch.post_name_transfer(body=body)
        return self.sign_encode_transaction(tx)

    def tx_name_revoke(self, name_id, fee, ttl):
        """
        create a revoke transaction
        :param name_id: the name to revoke
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        """
        nonce, ttl = self._get_nonce_ttl(ttl)
        body = dict(
            account_id=self.account.get_address(),
            name_id=name_id,
            ttl=ttl,
            fee=fee,
            nonce=nonce
        )
        tx = self.epoch.post_name_revoke(body=body)
        return self.sign_encode_transaction(tx)

    # CONTRACTS

    def tx_contract_create(self, code, call_data, amount, deposit, gas, gas_price, vm_version, fee, ttl):
        """
        create a revoke transaction
        :param name_id: the name to revoke
        :param fee: the transaction fee
        :param ttl: the ttl of the transaction
        """
        nonce, ttl = self._get_nonce_ttl(ttl)
        body = dict(
            owner_id=self.account.get_address(),
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
        tx = self.epoch.post_contract_create(body=body)
        t, s, th = self.sign_encode_transaction(tx)
        return t, s, th, tx.contract_id

    def tx_contract_call(self, contract_id, call_data, function, arg, amount, gas, gas_price, vm_version, fee, ttl):
        # compute the absolute ttl and the nonce
        nonce, ttl = self._get_nonce_ttl(ttl)
        body = dict(
            call_data=call_data,
            caller_id=self.account.get_address(),
            contract_id=contract_id,
            amount=amount,
            fee=fee,
            gas=gas,
            gas_price=gas_price,
            vm_version=vm_version,
            ttl=ttl,
            nonce=nonce
        )
        tx = self.epoch.post_contract_call(body=body)
        return self.sign_encode_transaction(tx)
