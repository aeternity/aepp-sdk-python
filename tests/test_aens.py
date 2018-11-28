from aeternity.aens import AEName
from tests import EPOCH_CLI, ACCOUNT, ACCOUNT_1, random_domain

from pytest import raises


def test_name_committment():
    domain = random_domain()
    name = EPOCH_CLI.AEName(domain)
    cl = name._get_commitment_id()
    cr = name.client.get_commitment_id(name=name.domain, salt=name.preclaim_salt)
    assert cl == cr.commitment_id


def test_name_validation_fails():
    with raises(ValueError):
        EPOCH_CLI.AEName('test.lol')


def test_name_validation_succeeds():
    EPOCH_CLI.AEName('test.test')


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
        name.preclaim(ACCOUNT)
        assert name.status == AEName.Status.PRECLAIMED
        name.claim(ACCOUNT)
        assert name.status == AEName.Status.CLAIMED
    except Exception as e:
        print(e)
        assert e is None


def test_name_status_unavailable():
    # claim a domain
    domain = random_domain()
    print(f"domain is {domain}")
    occupy_name = EPOCH_CLI.AEName(domain)
    occupy_name.full_claim_blocking(ACCOUNT)
    # try to get the same name
    same_name = EPOCH_CLI.AEName(domain)
    assert not same_name.is_available()


def test_name_update():
    # claim a domain
    domain = random_domain()
    print(f"domain is {domain}")
    name = EPOCH_CLI.AEName(domain)
    print("Claim name ", domain)
    name.full_claim_blocking(ACCOUNT)
    # domain claimed
    name.update_status()
    assert not EPOCH_CLI.AEName(domain).is_available(), 'The name should be claimed now'
    name.update_status()
    print("claimed name", name)
    print("pointers", name.pointers)
    assert len(name.pointers) > 0, 'Pointers should not be empty'
    assert name.pointers[0]['id'] == ACCOUNT.get_address()
    assert name.pointers[0]['key'] == "account_pubkey"


# TODO: enable the test check for pointers

def test_name_transfer_ownership():
    name = EPOCH_CLI.AEName(random_domain())
    name.full_claim_blocking(ACCOUNT)
    assert name.status == AEName.Status.CLAIMED
    name.update_status()
    assert name.pointers[0]['id'] == ACCOUNT.get_address()
    assert name.pointers[0]['key'] == "account_pubkey"

    # now transfer the name to the other account
    name.transfer_ownership(ACCOUNT, ACCOUNT_1.get_address())
    assert name.status == AEName.Status.TRANSFERRED
    # try changing the target using that new account
    name.update_status()
    name.update(ACCOUNT_1, ACCOUNT_1.get_address())
    name.update_status()
    assert len(name.pointers) > 0, 'Pointers should not be empty'
    assert name.pointers[0]['id'] == ACCOUNT_1.get_address()
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
    name.full_claim_blocking(ACCOUNT)
    name.revoke(ACCOUNT)
    assert name.status == AEName.Status.REVOKED
    assert EPOCH_CLI.AEName(domain).is_available()
