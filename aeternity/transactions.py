from aeternity import hashing
from aeternity.exceptions import TransactionHashMismatch

# RLP version number
# https://github.com/aeternity/protocol/blob/epoch-v0.10.1/serializations.md#binary-serialization
VSN = 1

# The list of tags can be found here:
# https://github.com/aeternity/protocol/blob/epoch-v0.10.1/serializations.md#table-of-object-tags
TAG_SIGNED_TX = 11
TAG_SPEND_TX = 12


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
        assert relative_ttl > 0
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

    def tx_contract_call(self, call_data, function, arg, amount, gas, gas_price, vm_version, fee, ttl):
        # compute the absolute ttl and the nonce
        nonce, ttl = self._get_nonce_ttl(ttl)
        body = dict(
            call_data=call_data,
            caller_id=self.account.get_address(),
            contract_id=self.address,
            amount=amount,
            fee=fee,
            gas=gas,
            gas_price=gas_price,
            vm_version=vm_version,
            ttl=ttl,
            nonce=nonce,
        )
        tx = self.epochent.cli.post_contract_call(body=body)
        return self.sign_encode_transaction(tx)
        
