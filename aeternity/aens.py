import json
import random
from _blake2 import blake2b

import base58
from base58 import b58encode_check

from aeternity.exceptions import NameNotAvailable, PreclaimFailed, TooEarlyClaim, MissingPreclaim
from aeternity.oracle import Oracle
from aeternity.epoch import EpochClient
from aeternity.openapi import OpenAPIClientException


# max number of block into the future that the name is going to be available
# https://github.com/aeternity/protocol/blob/epoch-v0.13.0/AENS.md#update
MAX_TTL = 36000
DEFAULT_NAME_TTL = 60000


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

        def hash_func(data): return blake2b(data, digest_size=32).digest()
        hashed = b'\x00' * 32
        while labels:
            hashed = hash_func(hashed + hash_func(labels[0]))
            labels = labels[1:]
        b58hash = base58.b58encode_check(hashed)
        return f'nm${b58hash}'

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
            print("update", response)
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

    def full_claim_blocking(self, keypair, preclaim_fee=1, claim_fee=1, update_fee=1, ttl=MAX_TTL, name_ttl=DEFAULT_NAME_TTL, target=None):
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
        :param ttl: the ttl for the name (in blocks)
        :param name_ttl: TODO: what is name ttl?
        :param target: the public key to associate the name to (pointers)
        """
        if not self.is_available():
            raise NameNotAvailable(self.domain)
        self.preclaim(keypair, fee=preclaim_fee)
        self.claim_blocking(keypair, fee=claim_fee)
        if target is None:
            target = keypair.get_address()
        self.update(keypair, target, fee=update_fee, ttl=ttl, name_ttl=name_ttl)

    def _get_commitment_hash(self, salt):
        response = self.client.cli.get_commitment_hash(name=self.domain, salt=salt)
        try:
            return response.commitment
        except KeyError:
            raise PreclaimFailed(response)

    def preclaim(self, keypair, fee=1, salt=None,):
        # check which block we used to create the preclaim
        self.preclaimed_block_height = self.client.get_height()
        if salt is not None:
            self.preclaim_salt = salt
        else:
            self.preclaim_salt = random.randint(0, 2**64)

        commitment_hash = self._get_commitment_hash(self.preclaim_salt)

        preclaim_transaction = self.client.cli.post_name_preclaim(body=dict(
            commitment=commitment_hash,
            fee=fee,
            account=keypair.get_address(),
        ))
        signed_transaction, b58signature = keypair.sign_transaction(preclaim_transaction)
        signed_transaction_reply = self.client.send_signed_transaction(signed_transaction)
        self.status = AEName.Status.PRECLAIMED
        return signed_transaction_reply.tx_hash, self.preclaim_salt

    def claim_blocking(self, keypair, fee=1):
        try:
            self.claim(keypair, fee=fee)
        except TooEarlyClaim:
            self.client.wait_for_next_block()
            self.claim(keypair, fee=fee)

    @classmethod
    def _encode_name(cls, name):
        if isinstance(name, str):
            name = name.encode('ascii')
        return 'nm$' + b58encode_check(name)

    def claim(self, keypair, fee=1):
        if self.preclaimed_block_height is None:
            raise MissingPreclaim('You must call preclaim before claiming a name')

        current_block_height = self.client.get_height()
        if self.preclaimed_block_height >= current_block_height:
            raise TooEarlyClaim(
                'You must wait for one block to call claim.'
                'Use `claim_blocking` if you have a lot of time on your hands'
            )

        claim_transaction = self.client.cli.post_name_claim(body=dict(
            account=keypair.get_address(),
            name=AEName._encode_name(self.domain),
            name_salt=self.preclaim_salt,
            fee=fee,
        ))

        tx_hash = self.client.post_transaction(keypair, claim_transaction)
        self.status = AEName.Status.CLAIMED
        return tx_hash, self.preclaim_salt

    def _get_pointers_json(self, target):
        if target.startswith('ak'):
            pointers = {'account_pubkey': target}
        else:
            pointers = {'oracle_pubkey': target}
        return json.dumps(pointers)

    def update(self, keypair, target, ttl=MAX_TTL, name_ttl=DEFAULT_NAME_TTL, fee=1):
        assert self.status == NameStatus.CLAIMED, 'Must be claimed to update pointer'

        if isinstance(target, Oracle):
            if target.oracle_id is None:
                raise ValueError('You must register the oracle before using it as target')
            target = target.oracle_id

        update_transaction = self.client.cli.post_name_update(body=dict(
            account=keypair.get_address(),
            name_hash=AEName.calculate_name_hash(self.domain),
            name_ttl=name_ttl,
            pointers=self._get_pointers_json(target),
            ttl=ttl,
            fee=fee,
        ))
        tx = self.client.post_transaction(keypair, update_transaction)
        signed_transaction, b58signature = keypair.sign_transaction(update_transaction)
        self.client.send_signed_transaction(signed_transaction)
        print(tx)
        # self.pointers = self._get_pointers_json(target),
        # TODO: why this one returns the whole transaction?
        return signed_transaction

    def transfer_ownership(self, keypair, receipient_pubkey, fee=1, name_ttl=600000,):
        transfer_transaction = self.client.cli.post_name_transfer(body=dict(
            account=keypair.get_address(),
            name_hash=self.get_name_hash(),
            recipient_pubkey=receipient_pubkey,
            fee=fee,

        ))

        signed_transaction, b58signature = keypair.sign_transaction(transfer_transaction)
        self.client.send_signed_transaction(signed_transaction)
        self.status = NameStatus.TRANSFERRED
        # TODO: why this one returns the whole transaction?
        return signed_transaction

    def revoke(self, keypair, fee=1):
        revoke_transaction = self.client.cli.post_name_revoke(body=dict(
            account=keypair.get_address(),
            name_hash=self.get_name_hash(),
            fee=fee,
        ))

        signed_transaction, b58signature = keypair.sign_transaction(revoke_transaction)
        self.client.send_signed_transaction(signed_transaction)
        self.status = NameStatus.REVOKED
        return signed_transaction
