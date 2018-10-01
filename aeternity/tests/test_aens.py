import random
import string

from pytest import raises

from aeternity.aens import AEName

from aeternity.tests import PUBLIC_KEY, PRIVATE_KEY, EPOCH_CLI

# to run this test in other environments set the env vars as specified in the
# config.py
from aeternity.signing import Account

# set the key folder as environment variables
account = Account.from_public_private_key_strings(PUBLIC_KEY, PRIVATE_KEY)


def random_domain(length=10):
    rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return rand_str + '.aet'


def test_name_committment():
    domain = random_domain()
    name = EPOCH_CLI.AEName(domain)
    cl = name._get_commitment_hash()
    cr = name.client.cli.get_commitment_id(name=name.domain, salt=name.preclaim_salt)
    assert cl == cr.commitment_id


def test_name_validation_fails():
    with raises(ValueError):
        EPOCH_CLI.AEName('test.lol')


def test_name_validation_succeeds():
    EPOCH_CLI.AEName('test.aet')


def test_name_is_available():
    name = EPOCH_CLI.AEName(random_domain())
    assert name.is_available()


def test_name_status_availavle():
    name = EPOCH_CLI.AEName(random_domain())
    assert name.status == AEName.Status.UNKNOWN
    name.update_status()
    assert name.status == AEName.Status.AVAILABLE


def test_name_claim_lifecycle():
    try:
        domain = random_domain()
        name = EPOCH_CLI.AEName(domain)
        assert name.status == AEName.Status.UNKNOWN
        name.update_status()
        assert name.status == AEName.Status.AVAILABLE
        name.preclaim(account)
        assert name.status == AEName.Status.PRECLAIMED
        name.claim(account)
        assert name.status == AEName.Status.CLAIMED
    except Exception as e:
        print(e)
        assert e is None


def test_name_status_unavailable():
    # claim a domain
    domain = random_domain()
    print(f"domain is {domain}")
    occupy_name = EPOCH_CLI.AEName(domain)
    occupy_name.full_claim_blocking(account, name_ttl=100)
    # try to get the same name
    same_name = EPOCH_CLI.AEName(domain)
    assert not same_name.is_available()


def test_name_update():
    # claim a domain
    domain = random_domain()
    print(f"domain is {domain}")
    name = EPOCH_CLI.AEName(domain)
    print("Claim name ", domain)
    name.full_claim_blocking(account, name_ttl=100)
    # domain claimed
    name.update_status()
    assert not EPOCH_CLI.AEName(domain).is_available(), 'The name should be claimed now'
    name.update_status()
    print("claimed name", name)
    print("pointers", name.pointers)
    assert len(name.pointers) > 0, 'Pointers should not be empty'
    assert name.pointers[0]['id'] == account.get_address()
    assert name.pointers[0]['key'] == "account_pubkey"


# TODO: enable the test check for pointers

def test_name_transfer_ownership():
    name = EPOCH_CLI.AEName(random_domain())
    name.full_claim_blocking(account, name_ttl=100)
    assert name.status == AEName.Status.CLAIMED
    name.update_status()
    assert name.pointers[0]['id'] == account.get_address()
    assert name.pointers[0]['key'] == "account_pubkey"

    new_key_pair = Account.generate()
    # put some coins into the account so the account is in the state tree
    # otherwise it couldn't become the owner of an address.
    EPOCH_CLI.spend(account, new_key_pair.get_address(), 100)
    # now transfer the name to the other account
    name.transfer_ownership(account, new_key_pair.get_address())
    assert name.status == AEName.Status.TRANSFERRED
    # try changing the target using that new account
    name.update_status()
    name.update(new_key_pair, target=new_key_pair.get_address(), name_ttl=10)
    name.update_status()
    assert len(name.pointers) > 0, 'Pointers should not be empty'
    assert name.pointers[0]['id'] == new_key_pair.get_address()
    assert name.pointers[0]['key'] == "account_pubkey"


# def test_transfer_failure_wrong_pubkey():
#     client = EpochClient()
#     name = EPOCH_CLI.AEName(random_domain())
#     name.full_claim_blocking()
#     client.wait_for_next_block()
#     with raises(AENSException):
#         name.transfer_ownership('ak_deadbeef')


def test_name_revocation():
    domain = random_domain()
    name = EPOCH_CLI.AEName(domain)
    name.full_claim_blocking(account, name_ttl=100)
    name.revoke(account=account)
    assert name.status == AEName.Status.REVOKED
    assert EPOCH_CLI.AEName(domain).is_available()
