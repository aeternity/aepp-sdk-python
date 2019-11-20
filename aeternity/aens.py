from aeternity.exceptions import NameNotAvailable, MissingPreclaim, NameUpdateError, NameTooEarlyClaim, NameCommitmentIdMismatch
from aeternity.openapi import OpenAPIClientException
from aeternity import defaults, identifiers, hashing, utils, transactions

import math


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
        self.name_id = hashing.name_id(domain)
        self.status = NameStatus.UNKNOWN
        # set after preclaimed:
        self.preclaimed_block_height = None
        self.preclaimed_tx_hash = None
        self.preclaimed_commitment_hash = None
        self.preclaim_salt = None
        # set after claimed
        self.name_ttl = 0
        self.pointers = None

    def __str__(self):
        return f"{self.domain}:{self.name_id}"

    @classmethod
    def validate_pointer(cls, pointer):
        return (
            not cls.validate_address(pointer, raise_exception=False)
            or
            not cls.validate_name(pointer, raise_exception=False)
        )

    @classmethod
    def get_minimum_name_fee(cls, domain: str) -> int:
        """
        Get the minimum name fee for a domain
        :param domain: the domain name to get the fee for
        :return: the minimum fee for the domain auction
        """
        name_len = len(domain.replace(".chain", ""))
        if name_len >= defaults.NAME_BID_MAX_LENGTH:
            return defaults.NAME_BID_RANGES.get(defaults.NAME_BID_MAX_LENGTH)
        return defaults.NAME_BID_RANGES.get(name_len)

    @classmethod
    def compute_bid_fee(cls, domain: str, start_fee: int = defaults.NAME_FEE, increment: float = defaults.NAME_FEE_BID_INCREMENT) -> int:
        """
        Get the minimum bid fee for a domain
        :param domain: the domain name to get the fee for
        :param start_fee: the start fee to calculate the min bid fee, if not provided the min_name_fee will be used as start fee
        :param increment: an increment in percentage in decimal notation (1)
        :return: the computed bid fee
        """
        if increment < defaults.NAME_FEE_BID_INCREMENT:
            raise TypeError(f"minimum increment percentage is {defaults.NAME_FEE_BID_INCREMENT}")
        if start_fee == defaults.NAME_FEE:
            start_fee = AEName.get_minimum_name_fee(domain)
        return math.ceil(start_fee * (1 + defaults.NAME_FEE_BID_INCREMENT))

    @classmethod
    def compute_auction_end_block(cls, domain: str, claim_height: int) -> int:
        """
        Given a domain name and a height compute the height when an auction will end
        :param domain: the domain name to get the auction end
        :param claim_height: height of the last claim for the domain name
        """
        name_len = len(domain) - 4
        if name_len < 4:
            return defaults.NAME_BID_TIMEOUTS.get(1) + claim_height
        if name_len < 8:
            return defaults.NAME_BID_TIMEOUTS.get(4) + claim_height
        if name_len <= defaults.NAME_BID_MAX_LENGTH:
            return defaults.NAME_BID_TIMEOUTS.get(8) + claim_height
        return claim_height

    def _get_pointers(self, targets):
        """
        Create a list of pointers given a list of addresses
        """
        pointers = []
        for t in targets:
            if isinstance(t, tuple):
                # custom target
                pointers.append({'key': t[0], 'id': t[1]})
            elif utils.is_valid_hash(t, prefix=identifiers.ACCOUNT_ID):
                pointers.append({'id': t, 'key': 'account_pubkey'})
            elif utils.is_valid_hash(t, prefix=identifiers.ORACLE_ID):
                pointers.append({'id': t, 'key': 'oracle_pubkey'})
            elif utils.is_valid_hash(t, prefix=identifiers.CONTRACT_ID):
                pointers.append({'id': t, 'key': 'contract_pubkey'})
            else:
                raise TypeError(f"invalid aens update pointer target {t}")
        return pointers

    def update_status(self):
        try:
            # use the Openapi client inside the node client
            response = self.client.get_name_entry_by_name(name=self.domain)
            self.status = NameStatus.CLAIMED
            self.name_ttl = response.ttl
            self.pointers = response.pointers
        except OpenAPIClientException as e:
            # e.g. if the status is already PRE-CLAIMED or CLAIMED, don't reset
            # it to AVAILABLE.
            self.name_ttl = 0
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

    def full_claim_blocking(self, account, *targets,
                            name_ttl=defaults.NAME_MAX_TTL,
                            client_ttl=defaults.NAME_MAX_CLIENT_TTL,
                            tx_ttl=defaults.TX_TTL):
        """
        Execute a name claim and updates the pointer to it.

        It executes:
        1. pre-claim
        2. claim
        3. pointers update

        :param account: the account registering the name
        :param targets: the  name pointer targets to associate to the name
        :param pre-claim_fee: the fee for the pre-claiming operation
        :param claim_fee: the fee for the claiming operation
        :param update_fee: the fee for the update operation
        :param tx_ttl: the ttl for the transaction
        :param name_ttl: the ttl of the name (in blocks)
        """
        # set the blocking to true
        blocking_orig = self.client.config.blocking_mode
        self.client.config.blocking_mode = True
        #
        if not self.is_available():
            raise NameNotAvailable(self.domain)
        hashes = {}
        # run pre-claim
        tx = self.preclaim(account)
        hashes['preclaim_tx'] = tx
        # wait for the block confirmation
        self.client.wait_for_confirmation(tx.hash)
        # run claim
        tx = self.claim(tx.hash, account, tx.metadata.salt)
        # wait for the block confirmation
        self.client.wait_for_confirmation(tx.hash)
        hashes['claim_tx'] = tx
        # run update
        tx = self.update(account, *targets, name_ttl=name_ttl, client_ttl=client_ttl)
        hashes['update_tx'] = tx
        # restore blocking value
        self.client.config.blocking_mode = blocking_orig
        return hashes

    def preclaim(self, account, fee=defaults.FEE, tx_ttl=defaults.TX_TTL) -> transactions.TxObject:
        """
        Execute a name pre-claim transaction

        :param account: the account performing the pre-claim
        :param fee: the fee for the transaction, [optional, calculated automatically]
        :param tx_ttl: relative number of blocks for the validity of the transaction

        :return: the TxObject of the pre-claim transaction including the parameters to
          calculate the commitment_id in the meta-data
        """
        # parse the fee
        fee = utils.amount_to_aettos(fee)
        # check which block we used to create the pre-claim
        self.preclaimed_block_height = self.client.get_current_key_block_height()
        # calculate the commitment id
        commitment_id, self.preclaim_salt = hashing.commitment_id(self.domain)
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create spend_tx
        tx = txb.tx_name_preclaim(account.get_address(), commitment_id, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx, metadata={"salt": self.preclaim_salt})
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed)
        # update local status
        self.status = AEName.Status.PRECLAIMED
        self.preclaim_tx_hash = tx_signed.hash
        return tx_signed

    def claim(self, preclaim_tx_hash, account, name_salt,
              name_fee=defaults.NAME_FEE,
              fee=defaults.FEE,
              tx_ttl=defaults.TX_TTL) -> transactions.TxObject:
        """
        Create and executes a claim transaction; performs a preliminary check
        to verify that the pre-claim exists and it has been confirmed

        :param preclaim_tx_hash: the transaction hash of the pre-claim transaction
        :param account: the account performing the transaction
        :param name_salt: the salt used to calculated the commitment_id in the pre-claim phase
        :param name_fee: the initial fee for the claim [optional, automatically calculated]
        :param fee: the fee for the transaction, [optional, calculated automatically]
        :param tx_ttl: relative number of blocks for the validity of the transaction

        :return: the TxObject of the claim

        :raises MissingPreclaim: if the pre-claim transaction cannot be found
        :raises NameCommitmentIdMismatch: if the commitment_id does not match the one from the pre-claim transaction
        :raises NameTooEarlyClaim: if the pre-claim transaction has not been confirmed yet
        :raises TypeError: if the value of the name_fee is not sufficient to successfully execute the claim
        """
        self.preclaim_salt = name_salt
        # parse the amounts
        name_fee, fee = utils._amounts_to_aettos(name_fee, fee)
        # get the pre-claim height
        try:
            pre_claim_tx = self.client.get_transaction_by_hash(hash=preclaim_tx_hash)
            self.preclaimed_block_height = pre_claim_tx.block_height
        except OpenAPIClientException:
            raise MissingPreclaim(f"Pre-claim transaction {preclaim_tx_hash} not found")
        # first get the protocol version
        protocol = self.client.get_consensus_protocol_version()
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
        # check the protocol version
        if protocol < identifiers.PROTOCOL_LIMA:
            tx = txb.tx_name_claim(account.get_address(), self.domain, self.preclaim_salt, fee, ttl, nonce)
        else:
            min_name_fee = AEName.get_minimum_name_fee(self.domain)
            if name_fee != defaults.NAME_FEE and name_fee < min_name_fee:
                raise TypeError(f"the provided fee {name_fee} is not enough to execute the claim, required: {min_name_fee}")
            name_fee = max(min_name_fee, name_fee)
            tx = txb.tx_name_claim_v2(account.get_address(), self.domain, self.preclaim_salt, name_fee, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed)
        # update status
        self.status = AEName.Status.CLAIMED
        return tx_signed

    def bid(self, account, bid_fee, fee=defaults.FEE, tx_ttl=defaults.TX_TTL) -> transactions.TxObject:
        """
        Implements bidding for a name, the precondition are:
        the name has been claimed and bidding is allowed, meaning that
        the auction is still active.

        As for the bidding parameters, both  fee_multiplier and bid_fee can be set,
        the actual bid value will be selected by max(current_name_fee*fee_multiplier, bid_fee).

        If no parameter is set the bidding strategy is to bid the minimum required by protocol

        :param account: the account performing the transaction
        :param bid_fee: the amount for the bid
        :param fee: the fee for the transaction, [optional, calculated automatically]
        :param tx_ttl: relative number of blocks for the validity of the transaction

        :return: the TxObject of the bid (same of claim)
        """
        txb = self.client.tx_builder
        # parse amounts
        bid_fee, fee = utils._amounts_to_aettos(bid_fee, fee)
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # check the protocol version
        tx = txb.tx_name_claim_v2(account.get_address(), self.domain, 0, bid_fee, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed)
        # update status
        self.status = AEName.Status.CLAIMED
        return tx_signed

    def update(self, account, *targets,
               name_ttl=defaults.NAME_MAX_TTL,
               client_ttl=defaults.NAME_MAX_CLIENT_TTL,
               fee=defaults.FEE,
               tx_ttl=defaults.TX_TTL):
        """
        Update a claimed name, an update may update the name_ttl and/or set name pointers for it.
        A name pointer can be specified as an address for accounts, oracles or contracts or using a custom
        tuple  containing the (key, value) for the pointer.

        :param account: the account singing the update transaction
        :param targets: the list of pointers targets
        :param name_ttl: the number of blocks before the name enters in the revoked state
        :param client_ttl: the ttl for client to cache the name in seconds
        :param fee: the fee for the transaction, [optional, calculated automatically]
        :param tx_ttl: relative number of blocks for the validity of the transaction

        :return: the TxObject of the update transaction

        :raises NameUpdateError: if the name is not claimed
        """
        if not self.check_claimed():
            raise NameUpdateError(f"the name {self.domain} must be claimed for an update transaction to be successful")
        # parse amounts
        fee = utils.amount_to_aettos(fee)
        # check that there are at least one target
        pointers = self._get_pointers(targets)
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_update(account.get_address(), self.name_id, pointers, name_ttl, client_ttl, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed)
        return tx_signed

    def transfer_ownership(self, account, recipient_id, fee=defaults.FEE, tx_ttl=defaults.TX_TTL):
        """
        Transfer ownership of a name to another account

        :param account: the account singing the transfer transaction and owner of the name
        :param recipient_id: the recipient of the name transfer that will become the new owner
        :param fee: the fee for the transaction, [optional, calculated automatically]
        :param tx_ttl: relative number of blocks for the validity of the transaction

        :return: the TxObject of the transfer transaction

        :raises NameUpdateError: if the name is not claimed
        """
        if not self.check_claimed():
            raise NameUpdateError(f"the name {self.domain} must be claimed for an update transaction to be successful")
        # get the transaction builder
        txb = self.client.tx_builder
        # parse amounts
        fee = utils.amount_to_aettos(fee)
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_transfer(account.get_address(), self.name_id, recipient_id, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed)
        # update the status
        self.status = NameStatus.TRANSFERRED
        return tx_signed

    def revoke(self, account, fee=defaults.FEE, tx_ttl=defaults.TX_TTL):
        """
        Revoke a registered name

        :param account: the account singing the revoke transaction and owner of the name
        :param fee: the fee for the transaction, [optional, calculated automatically]
        :param tx_ttl: relative number of blocks for the validity of the transaction

        :return: the TxObject of the revoke transaction

        :raises NameUpdateError: if the name is not claimed
        """
        if not self.check_claimed():
            raise NameUpdateError(f"the name {self.domain} must be claimed for an update transaction to be successful")
        # get the transaction builder
        txb = self.client.tx_builder
        # get the account nonce and ttl
        nonce, ttl = self.client._get_nonce_ttl(account.get_address(), tx_ttl)
        # create transaction
        tx = txb.tx_name_revoke(account.get_address(), self.name_id, fee, ttl, nonce)
        # sign the transaction
        tx_signed = self.client.sign_transaction(account, tx)
        # post the transaction to the chain
        self.client.broadcast_transaction(tx_signed)
        # update the status
        self.status = NameStatus.REVOKED
        return tx_signed
