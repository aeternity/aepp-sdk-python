from aeternity.exceptions import NameNotAvailable, MissingPreclaim, NameUpdateError
from aeternity.openapi import OpenAPIClientException
from aeternity.config import DEFAULT_TX_TTL, DEFAULT_FEE, DEFAULT_NAME_TTL, NAME_CLIENT_TTL
from aeternity import hashing, utils, oracles


class NameStatus:
    REVOKED = 'REVOKED'
    UNKNOWN = 'UNKNOWN'
    AVAILABLE = 'AVAILABLE'
    PRECLAIMED = 'PRECLAIMED'
    CLAIMED = 'CLAIMED'
    TRANSFERRED = 'TRANSFERRED'


class AEName:
    Status = NameStatus

    def __init__(self, domain, client):

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
    def _get_name_id(cls, name):
        """
        Compute the name id
        """
        if isinstance(name, str):
            name = name.encode('ascii')
        return hashing.encode('nm', name)

    def _get_commitment_id(self):
        """
        Compute the commitment id
        """
        self.preclaim_salt = hashing.randint()
        commitment_id = hashing.hash_encode("cm", hashing.namehash(self.domain) + self.preclaim_salt.to_bytes(32, 'big'))
        return commitment_id

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
        t, s, g, h = self.preclaim(account, fee=preclaim_fee, tx_ttl=tx_ttl)
        hashes['preclaim_tx'] = [t, s, g, h]
        # run claim
        t, s, g, h = self.claim(account, fee=claim_fee, tx_ttl=tx_ttl)
        hashes['claim_tx'] = [t, s, g, h]
        # target is the same of account is not specified
        if target is None:
            target = account.get_address()
        # run update
        t, s, g, h = self.update(account, target, fee=update_fee, name_ttl=name_ttl, client_ttl=client_ttl)
        hashes['update_tx'] = [t, s, g, h]
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
        commitment_id = self._get_commitment_id()
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create spend_tx
        tx = txb.tx_name_preclaim(account.get_address(), commitment_id, fee, ttl, nonce)
        # sign the transaction
        tx_signed, sg, tx_hash = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed, tx_hash)
        # update local status
        self.status = AEName.Status.PRECLAIMED
        self.preclaim_tx_hash = tx_hash
        return tx, tx_signed, sg, tx_hash

    def claim(self, account, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        if self.preclaimed_block_height is None:
            raise MissingPreclaim('You must call preclaim before claiming a name')
        # name encoded
        name = AEName._get_name_id(self.domain)
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_claim(account.get_address(), name, self.preclaim_salt, fee, ttl, nonce)
        # sign the transaction
        tx_signed, sg, tx_hash = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed, tx_hash)
        # update status
        self.status = AEName.Status.CLAIMED
        return tx, tx_signed, sg, tx_hash

    def update(self, account, target,
               name_ttl=DEFAULT_NAME_TTL,
               client_ttl=NAME_CLIENT_TTL,
               fee=DEFAULT_FEE,
               tx_ttl=DEFAULT_TX_TTL):

        if self.status != NameStatus.CLAIMED:
            raise NameUpdateError('Must be claimed to update pointer')

        if isinstance(target, oracles.Oracle):
            if target.oracle_id is None:
                raise ValueError('You must register the oracle before using it as target')
            target = target.oracle_id
        # get the name_id and pointers
        name_id = hashing.namehash_encode("nm", self.domain)
        pointers = self._get_pointers(target)
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_update(account.get_address(), name_id, pointers, name_ttl, client_ttl, fee, ttl, nonce)
        # sign the transaction
        tx_signed, sg, tx_hash = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed, tx_hash)
        return tx, tx_signed, sg, tx_hash

    def transfer_ownership(self, account, recipient_pubkey, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        """
        transfer ownership of a name
        :return: the transaction
        """
        # get the name_id and pointers
        name_id = hashing.namehash_encode("nm", self.domain)
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_transfer(account.get_address(), name_id, recipient_pubkey, fee, ttl, nonce)
        # sign the transaction
        tx_signed, sg, tx_hash = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed, tx_hash)
        # update the status
        self.status = NameStatus.TRANSFERRED
        return tx, tx_signed, sg, tx_hash

    def revoke(self, account, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        """
        revoke a name
        :return: the transaction
        """
        # get the name_id and pointers
        name_id = hashing.namehash_encode("nm", self.domain)
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_revoke(account.get_address(), name_id, fee, ttl, nonce)
        # sign the transaction
        tx_signed, sg, tx_hash = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed, tx_hash)
        # update the status
        self.status = NameStatus.REVOKED
        return tx_hash
