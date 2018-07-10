import json
import random

from aeternity.exceptions import NameNotAvailable, TooEarlyClaim, MissingPreclaim  # ,PreclaimFailed
from aeternity.oracle import Oracle
from aeternity.epoch import EpochClient
from aeternity.openapi import OpenAPIClientException
from aeternity.config import DEFAULT_TX_TTL, DEFAULT_FEE, NAME_MAX_TLL, NAME_DEFAULT_TTL
from aeternity.signing import hash, hash_encode, encode


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
            client = EpochClient()
        self.__class__.validate_name(domain)

        self.client = client
        self.domain = domain.lower()
        self.status = NameStatus.UNKNOWN
        # set after preclaimed:
        self.preclaimed_block_height = None
        self.preclaimed_commitment_hash = None
        self.preclaim_salt = None
        # set after claimed
        self.name_ttl = 0
        self.pointers = []

    @property
    def b58_name(self):
        return self._encode_name(self.domain)

    def get_name_hash(self):
        return AEName.calculate_name_hash(self.domain)

    @classmethod
    def calculate_name_hash(cls, name):
        if isinstance(name, str):
            name = name.encode('ascii')
        # see:
        # https://github.com/aeternity/protocol/blob/master/AENS.md#hashing
        # and also:
        # https://github.com/ethereum/EIPs/blob/master/EIPS/eip-137.md#namehash-algorithm
        labels = name.split(b'.')
        hashed = b'\x00' * 32
        while labels:
            hashed = hash(hashed + hash(labels[0]))
            labels = labels[1:]
        return encode("nm", hashed)

    @classmethod
    def validate_pointer(cls, pointer):
        return (
            not cls.validate_address(pointer, raise_exception=False)
            or
            not cls.validate_name(pointer, raise_exception=False)
        )

    @classmethod
    def validate_address(cls, address, raise_exception=True):
        if not address.startswith(('ak$', 'ok$')):
            if raise_exception:
                raise ValueError(
                    'pointer addresses must start with in ak$'
                )
            return False
        return True

    @classmethod
    def validate_name(cls, domain, raise_exception=True):
        # TODO: validate according to the spec!
        # TODO: https://github.com/aeternity/protocol/blob/master/AENS.md#name
        if not domain.endswith(('.aet', '.test')):
            if raise_exception:
                raise ValueError('AENS TLDs must end in .aet')
            return False
        return True

    def update_status(self):
        try:
            # use the openapi client inside the epoch client
            response = self.client.cli.get_name(name=self.domain)
            self.status = NameStatus.CLAIMED
            self.name_ttl = response.name_ttl
            self.pointers = json.loads(response.pointers)
        except OpenAPIClientException:
            # e.g. if the status is already PRECLAIMED or CLAIMED, don't reset
            # it to AVAILABLE.
            if self.status == NameStatus.UNKNOWN:
                self.status = NameStatus.AVAILABLE

    def is_available(self):
        self.update_status()
        return self.status == NameStatus.AVAILABLE

    def check_claimed(self):
        self.update_status()
        return self.status == NameStatus.CLAIMED

    def full_claim_blocking(self, keypair,
                            preclaim_fee=DEFAULT_FEE,
                            claim_fee=DEFAULT_FEE,
                            update_fee=DEFAULT_FEE,
                            name_ttl=NAME_MAX_TLL,
                            client_ttl=NAME_DEFAULT_TTL, target=None,
                            tx_ttl=DEFAULT_TX_TTL):
        """
        execute a name claim and updates the pointer to it.

        It executes:
        1. preclaim
        2. claim
        3. pointers update

        :param keypair: the keypair of the account registering the name
        :param preclaim_fee: the fee for the preclaiming operation
        :param claim_fee: the fee for the claiming operation
        :param update_fee: the fee for the update operation
        :param tx_ttl: the ttl for the transaction
        :param name_ttl: the ttl of the name (in blocks)
        :param target: the public key to associate the name to (pointers)
        """
        if not self.is_available():
            raise NameNotAvailable(self.domain)
        self.preclaim(keypair, fee=preclaim_fee, tx_ttl=tx_ttl)
        self.claim_blocking(keypair, fee=claim_fee, tx_ttl=tx_ttl)
        if target is None:
            target = keypair.get_address()
        self.update(keypair, target, fee=update_fee, name_ttl=name_ttl, client_ttl=name_ttl)

    def _get_commitment_hash(self):
        """Calculate the commitment hash"""
        self.preclaim_salt = random.randint(0, 2**64)
        name_digest = hash(data=self.domain.encode("ascii"))
        commitment = hash_encode("cm", name_digest + self.preclaim_salt.to_bytes(32, 'big'))
        return commitment

    def preclaim(self, keypair, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        """
        Execute a name preclaim
        """
        # check which block we used to create the preclaim
        self.preclaimed_block_height = self.client.get_height()
        # calculate the commitment hash
        commitment_hash = self._get_commitment_hash()
        # compute the absolute ttl
        ttl = self.client.compute_absolute_ttl(tx_ttl)
        # preclaim
        preclaim_transaction = self.client.cli.post_name_preclaim(body=dict(
            commitment=commitment_hash,
            fee=fee,
            account=keypair.get_address(),
            ttl=ttl
        ))
        signed_tx = self.client.post_transaction(keypair, preclaim_transaction)
        self.status = AEName.Status.PRECLAIMED
        return signed_tx.tx_hash, self.preclaim_salt

    def claim_blocking(self, keypair, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        try:
            self.claim(keypair, fee=fee, tx_ttl=tx_ttl)
        except TooEarlyClaim:
            self.client.wait_for_next_block()
            self.claim(keypair, fee=fee, tx_ttl=tx_ttl)

    @classmethod
    def _encode_name(cls, name):
        if isinstance(name, str):
            name = name.encode('ascii')
        return encode('nm', name)

    def claim(self, keypair, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        if self.preclaimed_block_height is None:
            raise MissingPreclaim('You must call preclaim before claiming a name')

        current_block_height = self.client.get_height()
        if self.preclaimed_block_height >= current_block_height:
            raise TooEarlyClaim(
                'You must wait for one block to call claim.'
                'Use `claim_blocking` if you have a lot of time on your hands'
            )
        # compute the absolute ttl
        ttl = self.client.compute_absolute_ttl(tx_ttl)
        claim_transaction = self.client.cli.post_name_claim(body=dict(
            account=keypair.get_address(),
            name=AEName._encode_name(self.domain),
            name_salt=self.preclaim_salt,
            fee=fee,
            ttl=ttl
        ))

        signed_tx = self.client.post_transaction(keypair, claim_transaction)
        self.status = AEName.Status.CLAIMED
        return signed_tx.tx_hash, self.preclaim_salt

    def _get_pointers_json(self, target):
        if target.startswith('ak'):
            pointers = {'account_pubkey': target}
        else:
            pointers = {'oracle_pubkey': target}
        return json.dumps(pointers)

    def update(self, keypair, target,
               name_ttl=NAME_MAX_TLL,
               client_ttl=NAME_DEFAULT_TTL,
               fee=DEFAULT_FEE,
               tx_ttl=DEFAULT_TX_TTL):
        assert self.status == NameStatus.CLAIMED, 'Must be claimed to update pointer'

        if isinstance(target, Oracle):
            if target.oracle_id is None:
                raise ValueError('You must register the oracle before using it as target')
            target = target.oracle_id

        # compute the absolute ttl
        ttl = self.client.compute_absolute_ttl(tx_ttl)
        # send the update transaction
        update_transaction = self.client.cli.post_name_update(body=dict(
            account=keypair.get_address(),
            name_hash=AEName.calculate_name_hash(self.domain),
            client_ttl=client_ttl,
            name_ttl=name_ttl,
            pointers=self._get_pointers_json(target),
            ttl=ttl,
            fee=fee,
        ))
        return self.client.post_transaction(keypair, update_transaction)

    def transfer_ownership(self, keypair, receipient_pubkey,
                           fee=DEFAULT_FEE,
                           name_ttl=NAME_DEFAULT_TTL,
                           tx_ttl=DEFAULT_TX_TTL):
        """
        transfer ownership of a name
        :return: the transaction
        """
        # compute the absolute ttl
        ttl = self.client.compute_absolute_ttl(tx_ttl)
        transfer_transaction = self.client.cli.post_name_transfer(body=dict(
            account=keypair.get_address(),
            name_hash=self.get_name_hash(),
            recipient_pubkey=receipient_pubkey,
            ttl=ttl,
            fee=fee,
        ))
        signed_tx = self.client.post_transaction(keypair, transfer_transaction)
        self.status = NameStatus.TRANSFERRED
        return signed_tx

    def revoke(self, keypair, fee=DEFAULT_FEE, tx_ttl=DEFAULT_TX_TTL):
        """
        transfer ownership of a name
        :return: the transaction
        """
        # compute the absolute ttl
        ttl = self.client.compute_absolute_ttl(tx_ttl)
        revoke_transaction = self.client.cli.post_name_revoke(body=dict(
            account=keypair.get_address(),
            name_hash=self.get_name_hash(),
            fee=fee,
            ttl=ttl
        ))
        signed_tx = self.client.post_transaction(keypair, revoke_transaction)
        self.status = NameStatus.REVOKED
        return signed_tx
