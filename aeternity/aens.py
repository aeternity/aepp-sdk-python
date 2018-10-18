from aeternity.exceptions import NameNotAvailable, MissingPreclaim, NameUpdateError
from aeternity.openapi import OpenAPIClientException
from aeternity.config import DEFAULT_TX_TTL, DEFAULT_FEE, DEFAULT_NAME_TTL, NAME_CLIENT_TTL
from aeternity import hashing, utils, oracle, epoch
from aeternity.transactions import TxBuilder


class NameStatus:
    REVOKED = 'REVOKED'
    UNKNOWN = 'UNKNOWN'
    AVAILABLE = 'AVAILABLE'
    PRECLAIMED = 'PRECLAIMED'
    CLAIMED = 'CLAIMED'
    TRANSFERRED = 'TRANSFERRED'


class AEName:
    Status = NameStatus

    def __init__(self, domain, client=None):
        if client is None:
            client = epoch.EpochClient()
        if not utils.is_valid_aens_name(domain):
            raise ValueError("Invalid domain ", domain)

        self.client = client
        self.domain = domain.lower()
        self.status = NameStatus.UNKNOWN
        # set after preclaimed:
        self.preclaimed_block_height = None
        self.preclaimed_tx_hash = None
        self.preclaimed_commitment_hash = None
        self.preclaim_salt = None
        # set after claimed
        self.name_hash = None
        self.name_ttl = 0
        self.pointers = None

    @classmethod
    def validate_pointer(cls, pointer):
        return (
            not cls.validate_address(pointer, raise_exception=False)
            or
            not cls.validate_name(pointer, raise_exception=False)
        )

    @classmethod
    def _encode_name(cls, name):
        if isinstance(name, str):
            name = name.encode('ascii')
        return hashing.encode('nm', name)

    def _get_commitment_hash(self):
        """Calculate the commitment hash"""
        self.preclaim_salt = hashing.randint()
        commitment = hashing.hash_encode("cm", hashing.namehash(self.domain) + self.preclaim_salt.to_bytes(32, 'big'))
        return commitment

    def _get_pointers(self, target):
        if target.startswith('ak'):
            pointers = [{'id': target, 'key': 'account_pubkey'}]
        else:
            pointers = [{'id': target, 'key': 'oracle_pubkey'}]
        return pointers

    def update_status(self):
        try:
            # use the openapi client inside the epoch client
            response = self.client.get_name_entry_by_name(name=self.domain)
            self.status = NameStatus.CLAIMED
            self.name_ttl = response.ttl
            self.name_hash = response.id
            self.pointers = response.pointers
        except OpenAPIClientException as e:
            # e.g. if the status is already PRECLAIMED or CLAIMED, don't reset
            # it to AVAILABLE.
            self.name_ttl = 0
            self.name_hash = None
            self.pointers = None
            if e.code == 404:
                self.status = NameStatus.AVAILABLE
            if self.status == NameStatus.UNKNOWN:
                self.status = NameStatus.AVAILABLE

    def is_available(self):
        self.update_status()
        return self.status == NameStatus.AVAILABLE

    def check_claimed(self):
        self.update_status()
        return self.status == NameStatus.CLAIMED

    def full_claim_blocking(self, account,
                            preclaim_fee=DEFAULT_FEE,
                            claim_fee=DEFAULT_FEE,
                            update_fee=DEFAULT_FEE,
                            name_ttl=DEFAULT_NAME_TTL,
                            client_ttl=NAME_CLIENT_TTL,
                            target=None,
                            tx_ttl=DEFAULT_TX_TTL):
        """
        Execute a name claim and updates the pointer to it.

        It executes:
        1. preclaim
        2. claim
        3. pointers update

        :param account: the account registering the name
        :param preclaim_fee: the fee for the preclaiming operation
        :param claim_fee: the fee for the claiming operation
        :param update_fee: the fee for the update operation
        :param tx_ttl: the ttl for the transaction
        :param name_ttl: the ttl of the name (in blocks)
        :param target: the public key to associate the name to (pointers)
        """
        # set the blocking to true
        blocking_orig = self.client.blocking_mode
        self.client.blocking_mode = True
        #
        if not self.is_available():
            raise NameNotAvailable(self.domain)
        hashes = {}
        # run preclaim
        h = self.preclaim(account, fee=preclaim_fee, tx_ttl=tx_ttl)
        hashes['preclaim_tx'] = h
        # run claim
        h = self.claim(account, fee=claim_fee, tx_ttl=tx_ttl)
        hashes['claim_tx'] = h
        # target is the same of account is not specified
        if target is None:
            target = account.get_address()
        # run update
        h = self.update(account, target, fee=update_fee, name_ttl=name_ttl, client_ttl=client_ttl)
        hashes['update_tx'] = h
        # restore blocking value
        self.client.blocking_mode = blocking_orig
        return hashes

    def preclaim(self, account, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        """
        Execute a name preclaim
        """
        # check which block we used to create the preclaim
        self.preclaimed_block_height = self.client.get_current_key_block_height()
        # calculate the commitment hash
        commitment_hash = self._get_commitment_hash()
        # get the transaction builder
        txb = TxBuilder(self.client, account)
        # create spend_tx
        tx, sg, tx_hash = txb.tx_name_preclaim(commitment_hash, fee, tx_ttl)
        # post the transaction to the chain
        txb.post_transaction(tx, tx_hash)
        if self.client.blocking_mode:
            txb.wait_tx(tx_hash)
        # update local status
        self.status = AEName.Status.PRECLAIMED
        self.preclaim_tx_hash = tx_hash
        return tx_hash

    def claim(self, account, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        if self.preclaimed_block_height is None:
            raise MissingPreclaim('You must call preclaim before claiming a name')
        # name encoded TODO: shall this goes into transactions?
        name = AEName._encode_name(self.domain)
        # get the transaction builder
        txb = TxBuilder(self.client, account)
        # create claim transaction
        tx, sg, tx_hash = txb.tx_name_claim(name, self.preclaim_salt, fee, tx_ttl)
        # post the transaction to the chain
        txb.post_transaction(tx, tx_hash)
        # ensure tx
        if self.client.blocking_mode:
            txb.wait_tx(tx_hash)
        # update status
        self.status = AEName.Status.CLAIMED
        return tx_hash

    def update(self, account, target,
               name_ttl=DEFAULT_NAME_TTL,
               client_ttl=NAME_CLIENT_TTL,
               fee=DEFAULT_FEE,
               tx_ttl=DEFAULT_TX_TTL):

        if self.status != NameStatus.CLAIMED:
            raise NameUpdateError('Must be claimed to update pointer')

        if isinstance(target, oracle.Oracle):
            if target.oracle_id is None:
                raise ValueError('You must register the oracle before using it as target')
            target = target.oracle_id
        # TODO: check the value for name ttl?

        # get the name_id and pointers
        name_id = hashing.namehash_encode("nm", self.domain)
        pointers = self._get_pointers(target)
        # get the transaction builder
        txb = TxBuilder(self.client, account)
        # create claim transaction
        tx, sg, tx_hash = txb.tx_name_update(name_id, pointers, name_ttl, client_ttl, fee, tx_ttl)
        # post the transaction to the chain
        txb.post_transaction(tx, tx_hash)
        # ensure tx
        if self.client.blocking_mode:
            txb.wait_tx(tx_hash)
        return tx_hash

    def transfer_ownership(self, account, recipient_pubkey, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        """
        transfer ownership of a name
        :return: the transaction
        """
        # get the name_id and pointers
        name_id = hashing.namehash_encode("nm", self.domain)
        # get the transaction builder
        txb = TxBuilder(self.client, account)
        # create claim transaction
        tx, sg, tx_hash = txb.tx_name_transfer(name_id, recipient_pubkey, fee, tx_ttl)
        # post the transaction to the chain
        txb.post_transaction(tx, tx_hash)
        # update local status
        self.status = NameStatus.TRANSFERRED
        # ensure tx
        if self.client.blocking_mode:
            txb.wait_tx(tx_hash)
        return tx_hash

    def revoke(self, account, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        """
        revoke a name
        :return: the transaction
        """
        # get the name_id and pointers
        name_id = hashing.namehash_encode("nm", self.domain)
        # get the transaction builder
        txb = TxBuilder(self.client, account)
        # create claim transaction
        tx, sg, tx_hash = txb.tx_name_revoke(name_id, fee, tx_ttl)
        # post the transaction to the chain
        txb.post_transaction(tx, tx_hash)
        # ensure tx
        if self.client.blocking_mode:
            txb.wait_tx(tx_hash)
        self.status = NameStatus.REVOKED
        return tx_hash
