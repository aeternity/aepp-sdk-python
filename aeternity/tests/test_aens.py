import random
import string

from pytest import raises

from aeternity.epoch import EpochClient
from aeternity.aens import AEName

from aeternity.tests import PUBLIC_KEY, PRIVATE_KEY

# to run this test in other environments set the env vars as specified in the
# config.py
from aeternity.signing import KeyPair

# set the key folder as environment variables
keypair = KeyPair.from_public_private_key_strings(PUBLIC_KEY, PRIVATE_KEY)


def random_domain(length=10):
    rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return rand_str + '.aet'


def test_committment():
    domain = random_domain()
    name = AEName(domain)
    cl = name._get_commitment_hash()
    cr = name.client.cli.get_commitment_hash(name=name.domain, salt=name.preclaim_salt)
    assert cl == cr.commitment


def test_name_validation_fails():
    with raises(ValueError):
        AEName('test.lol')


def test_name_validation_succeeds():
    AEName('test.aet')


def test_name_is_available():
    name = AEName(random_domain())
    assert name.is_available()


def test_name_status_availavle():
    name = AEName(random_domain())
    assert name.status == AEName.Status.UNKNOWN
    name.update_status()
    assert name.status == AEName.Status.AVAILABLE


def test_name_hashing():
    assert AEName.calculate_name_hash('welghmolql.aet') == 'nm$2KrC4asc6fdv82uhXDwfiqB1TY2htjhnzwzJJKLxidyMymJRUQ'


def test_name_claim_lifecycle():
    domain = random_domain()
    name = AEName(domain)
    assert name.status == AEName.Status.UNKNOWN
    name.update_status()
    assert name.status == AEName.Status.AVAILABLE
    name.preclaim(keypair)
    assert name.status == AEName.Status.PRECLAIMED
    name.claim_blocking(keypair)
    assert name.status == AEName.Status.CLAIMED


def test_name_status_unavailable():
    # claim a domain
    domain = random_domain()
    occupy_name = AEName(domain)
    occupy_name.full_claim_blocking(keypair, name_ttl=70)
    # wait for the state to propagate in the block chain
    EpochClient().wait_for_next_block()
    same_name = AEName(domain)
    assert not same_name.is_available()


def test_name_update():
    client = EpochClient()
    # claim a domain
    domain = random_domain()
    print(f"domain is {domain}")
    name = AEName(domain)
    print("Claim name ", domain)
    name.full_claim_blocking(keypair, name_ttl=70)
    print("got next block")
    client.wait_n_blocks(2)
    print("got next block")
    assert not AEName(domain).is_available(), 'The name should be claimed now'
    name.update_status()
    client.wait_n_blocks(2)
    name.update_status()
    print("claimed name", name)
    assert name.pointers != [], 'Pointers should not be empty'
    assert name.pointers['account_pubkey'] == keypair.get_address()


# TODO: enable the test check for pointers

def test_name_transfer_ownership():
    client = EpochClient()
    name = AEName(random_domain())
    name.full_claim_blocking(keypair, name_ttl=70)
    assert name.status == AEName.Status.CLAIMED
    client.wait_for_next_block()

    new_key_pair = KeyPair.generate()
    # put some coins into the account so the account is in the state tree
    # otherwise it couldn't become the owner of an address.
    client.spend(keypair, new_key_pair.get_address(), 1)
    client.wait_for_next_block()
    # now transfer the name to the other account
    name.transfer_ownership(keypair, new_key_pair.get_address())
    assert name.status == AEName.Status.TRANSFERRED
    client.wait_for_next_block()
    # try changing the target using that new keypair
    name.update_status()
    name.update(new_key_pair, target=new_key_pair.get_address(), name_ttl=10)
    client.wait_for_next_block()
    name.update_status()
    assert name.pointers != [], 'Pointers should not be empty'
    assert name.pointers['account_pubkey'] == new_key_pair.get_address()

# def test_transfer_failure_wrong_pubkey():
#     client = EpochClient()
#     name = AEName(random_domain())
#     name.full_claim_blocking()
#     client.wait_for_next_block()
#     with raises(AENSException):
#         name.transfer_ownership('ak$deadbeef')


def test_name_revocation():
    domain = random_domain()
    name = AEName(domain)
    name.full_claim_blocking(keypair, name_ttl=10)
    EpochClient().wait_for_next_block()
    name.revoke(keypair=keypair)
    assert name.status == AEName.Status.REVOKED
    EpochClient().wait_for_next_block()
    assert AEName(domain).is_available()
