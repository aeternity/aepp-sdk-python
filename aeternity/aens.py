import json
import random

from aeternity.exceptions import NameNotAvailable, PreclaimFailed, TooEarlyClaim, ClaimFailed, AENSException, \
    UpdateError, MissingPreclaim, InsufficientFundsException, AException
from aeternity.oracle import Oracle
from aeternity.epoch import EpochClient

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
        self.domain = domain
        self.status = NameStatus.UNKNOWN
        # set after preclaimed:
        self.preclaimed_block_height = None
        self.preclaimed_commitment_hash = None
        self.preclaim_salt = None
        # set after claimed
        self.name_hash = None
        self.name_ttl = 0
        self.pointers = []

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
            response = self.client.local_http_get('name', params={'name': self.domain})
            self.status = NameStatus.CLAIMED
            self.name_hash = response['name_hash']
            self.name_ttl = response['name_ttl']
            self.pointers = json.loads(response['pointers'])
        except NameNotAvailable:
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

    def full_claim_blocking(self, preclaim_fee=1, claim_fee=1):
        if not self.is_available():
            raise NameNotAvailable(self.domain)
        self.preclaim(fee=preclaim_fee)
        self.claim_blocking(fee=claim_fee)

    def preclaim(self, fee=1, salt=None):
        # check which block we used to create the preclaim
        self.preclaimed_block_height = self.client.get_height()
        if salt is not None:
            self.preclaim_salt = salt
        else:
            self.preclaim_salt = random.randint(0, 2**64)
        response = self.client.local_http_get(
            'commitment-hash',
            params={
                'name': self.domain,
                'salt': self.preclaim_salt
            }
        )
        try:
            commitment_hash = response['commitment']
        except KeyError:
            raise PreclaimFailed(response)
        response = self.client.internal_http_post(
            'name-preclaim-tx',
            json={
                "commitment": commitment_hash,
                "fee": fee
            },
        )
        try:
            # the response is an empty dict if the call failed error
            self.preclaimed_commitment_hash = response['commitment']
            self.status = NameStatus.PRECLAIMED
        except KeyError:
            reason = response.get('reason')
            if reason == 'No funds in account':
                raise InsufficientFundsException(response)
            raise PreclaimFailed(response)
        return self.preclaimed_commitment_hash, self.preclaim_salt

    def claim_blocking(self, fee=1):
        try:
            self.claim(fee=fee)
        except TooEarlyClaim:
            self.client.wait_for_next_block()
            self.claim(fee=fee)

    def claim(self, fee=1):
        if self.preclaimed_block_height is None:
            raise MissingPreclaim('You must call preclaim before claiming a name')

        current_block_height = self.client.get_height()
        if self.preclaimed_block_height >= current_block_height:
            raise TooEarlyClaim(
                'You must wait for one block to call claim.'
                'Use `claim_blocking` if you have a lot of time on your hands'
            )

        response = self.client.internal_http_post(
            'name-claim-tx',
            json={
                'name': self.domain,
                'name_salt': self.preclaim_salt,
                'fee': fee
            }
        )
        try:
            self.name_hash = response['name_hash']
            self.status = AEName.Status.CLAIMED
        except KeyError:
            raise ClaimFailed(response)

    def update(self, target, ttl=50, fee=1):
        assert self.status == NameStatus.CLAIMED, 'Must be claimed to update pointer'

        if isinstance(target, Oracle):
            if target.oracle_id is None:
                raise ValueError('You must register the oracle before using it as target')
            target = target.oracle_id

        if target.startswith('ak'):
            pointers = {'account_pubkey': target}
        else:
            pointers = {'oracle_pubkey': target}

        response = self.client.internal_http_post(
            'name-update-tx',
            json={
                "name_hash": self.name_hash,
                "name_ttl": self.name_ttl,
                "ttl": ttl,
                "pointers": json.dumps(pointers),
                "fee": fee
            }
        )
        if 'name_hash' in response:
            self.pointers = pointers
        else:
            raise UpdateError(response)

    def transfer_ownership(self, receipient_pubkey, fee=1):
        response = self.client.internal_http_post(
            'name-transfer-tx',
            json={
                "name_hash": self.name_hash,
                "recipient_pubkey": receipient_pubkey,
                "fee": fee
            }
        )
        if 'name_hash' not in response:
            raise AENSException('transfer ownership failed', payload=response)
        self.status = NameStatus.TRANSFERRED

    def revoke(self, fee=1):
        response = self.client.internal_http_post(
            'name-revoke-tx',
            json={
                "name_hash": self.name_hash,
                "fee": fee
            }
        )
        if 'name_hash' in response:
            self.status = NameStatus.REVOKED
        else:
            raise AENSException('Error revoking name', payload=response)
