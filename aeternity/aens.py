from aeternity.exceptions import NameNotAvailable, MissingPreclaim, NameUpdateError, NameTooEarlyClaim, NameCommitmentIdMismatch
from aeternity.openapi import OpenAPIClientException
from aeternity import defaults
from aeternity import hashing, utils, oracles
from aeternity.identifiers import ACCOUNT_ID, NAME


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

    def _get_pointers(self, target):
        if target.startswith(ACCOUNT_ID):
            pointers = [{'id': target, 'key': 'account_pubkey'}]
        else:
            pointers = [{'id': target, 'key': 'oracle_pubkey'}]
        return pointers

    def update_status(self):
        try:
            # use the openapi client inside the node client
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
                            name_ttl=defaults.NAME_TTL,
                            client_ttl=defaults.NAME_CLIENT_TTL,
                            target=None,
                            tx_ttl=defaults.TX_TTL):
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
        blocking_orig = self.client.config.blocking_mode
        self.client.config.blocking_mode = True
        #
        if not self.is_available():
            raise NameNotAvailable(self.domain)
        hashes = {}
        # run preclaim
        tx = self.preclaim(account)
        hashes['preclaim_tx'] = tx
        # wait for the block confirmation
        self.client.wait_for_confirmation(tx.hash)
        # run claim
        tx = self.claim(account, tx.metadata.salt, tx.hash)
        hashes['claim_tx'] = tx
        # target is the same of account is not specified
        if target is None:
            target = account.get_address()
        # run update
        tx = self.update(account, target, name_ttl=name_ttl, client_ttl=client_ttl)
        hashes['update_tx'] = tx
        # restore blocking value
        self.client.config.blocking_mode = blocking_orig
        return hashes

    def preclaim(self, account, fee=defaults.FEE, tx_ttl=defaults.TX_TTL):
        """
        Execute a name preclaim
        """
        # check which block we used to create the preclaim
        self.preclaimed_block_height = self.client.get_current_key_block_height()
        # calculate the commitment hash
        commitment_id, self.preclaim_salt = hashing.commitment_id(self.domain)
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create spend_tx
        tx = txb.tx_name_preclaim(account.get_address(), commitment_id, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx.tx, metadata={"salt": self.preclaim_salt})
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed.tx, tx_signed.hash)
        # update local status
        self.status = AEName.Status.PRECLAIMED
        self.preclaim_tx_hash = tx_signed.hash
        return tx_signed

    def claim(self, account, name_salt, preclaim_tx_hash, fee=defaults.FEE, tx_ttl=defaults.TX_TTL):
        self.preclaim_salt = name_salt
        # get the preclaim height
        try:
            pre_claim_tx = self.client.get_transaction_by_hash(hash=preclaim_tx_hash)
            self.preclaimed_block_height = pre_claim_tx.block_height
        except OpenAPIClientException:
            raise MissingPreclaim(f"Preclaim transaction {preclaim_tx_hash} not found")
        # if the commitment_id mismatch
        pre_claim_commitment_id = pre_claim_tx.tx.commitment_id
        commitment_id, _ = hashing.commitment_id(self.domain, salt=name_salt)
        if pre_claim_commitment_id != commitment_id:
            raise NameCommitmentIdMismatch(f"Commitment id mismatch, wanted {pre_claim_commitment_id} got {commitment_id}")
        # if the transaction has not been mined
        if self.preclaimed_block_height <= 0:
            raise NameTooEarlyClaim(f"The pre-claim transaction has not been mined yet")
        # get the current height
        current_height = self.client.get_current_key_block_height()
        safe_height = self.preclaimed_block_height + self.client.config.key_block_confirmation_num
        if current_height < safe_height:
            raise NameTooEarlyClaim(f"It is not safe to execute the name claim before height {safe_height}, current height: {current_height}")
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_claim(account.get_address(), self.domain, self.preclaim_salt, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx.tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed.tx, tx_signed.hash)
        # update status
        self.status = AEName.Status.CLAIMED
        return tx_signed

    def update(self, account, target,
               name_ttl=defaults.NAME_TTL,
               client_ttl=defaults.NAME_CLIENT_TTL,
               fee=defaults.FEE,
               tx_ttl=defaults.TX_TTL):

        if not self.check_claimed():
            raise NameUpdateError('Must be claimed to update pointer')

        if isinstance(target, oracles.Oracle):
            if target.oracle_id is None:
                raise ValueError('You must register the oracle before using it as target')
            target = target.oracle_id
        # get the name_id and pointers
        name_id = hashing.namehash_encode(NAME, self.domain)
        pointers = self._get_pointers(target)
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_update(account.get_address(), name_id, pointers, name_ttl, client_ttl, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx.tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed.tx, tx_signed.hash)
        return tx_signed

    def transfer_ownership(self, account, recipient_pubkey, fee=defaults.FEE, tx_ttl=defaults.TX_TTL):
        """
        transfer ownership of a name
        :return: the transaction
        """
        # get the name_id and pointers
        name_id = hashing.namehash_encode(NAME, self.domain)
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_transfer(account.get_address(), name_id, recipient_pubkey, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx.tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed.tx, tx_signed.hash)
        # update the status
        self.status = NameStatus.TRANSFERRED
        return tx_signed

    def revoke(self, account, fee=defaults.FEE, tx_ttl=defaults.TX_TTL):
        """
        revoke a name
        :return: the transaction
        """
        # get the name_id and pointers
        name_id = hashing.namehash_encode(NAME, self.domain)
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_revoke(account.get_address(), name_id, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx.tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed.tx, tx_signed.hash)
        # update the status
        self.status = NameStatus.REVOKED
        return tx_signed
