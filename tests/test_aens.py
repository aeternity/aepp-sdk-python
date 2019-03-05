from aeternity.aens import AEName

from pytest import raises


def test_name_validation_fails(chain_fixture):
    with raises(ValueError):
        chain_fixture.NODE_CLI.AEName('test.lol')


def test_name_validation_succeeds(chain_fixture):
    chain_fixture.NODE_CLI.AEName('test.test')


def test_name_is_available(chain_fixture, random_domain):
    name = chain_fixture.NODE_CLI.AEName(random_domain)
    assert name.is_available()


def test_name_status_available(chain_fixture, random_domain):
    name = chain_fixture.NODE_CLI.AEName(random_domain)
    assert name.status == AEName.Status.UNKNOWN
    name.update_status()
    assert name.status == AEName.Status.AVAILABLE


def test_name_claim_lifecycle(chain_fixture, random_domain):
    try:
        domain = random_domain
        node_cli = chain_fixture.NODE_CLI
        name = node_cli.AEName(domain)
        assert name.status == AEName.Status.UNKNOWN
        name.update_status()
        assert name.status == AEName.Status.AVAILABLE
        preclaim = name.preclaim(chain_fixture.ACCOUNT)
        assert name.status == AEName.Status.PRECLAIMED
        node_cli.wait_for_confirmation(preclaim.hash)
        name.claim(chain_fixture.ACCOUNT, preclaim.metadata.salt, preclaim.hash)
        assert name.status == AEName.Status.CLAIMED
    except Exception as e:
        print(e)
        assert e is None


def test_name_status_unavailable(chain_fixture, random_domain):
    # claim a domain
    domain = random_domain
    print(f"domain is {domain}")
    occupy_name = chain_fixture.NODE_CLI.AEName(domain)
    occupy_name.full_claim_blocking(chain_fixture.ACCOUNT)
    # try to get the same name
    same_name = chain_fixture.NODE_CLI.AEName(domain)
    assert not same_name.is_available()


def test_name_update(chain_fixture, random_domain):
    # claim a domain
    domain = random_domain
    print(f"domain is {domain}")
    name = chain_fixture.NODE_CLI.AEName(domain)
    print("Claim name ", domain)
    name.full_claim_blocking(chain_fixture.ACCOUNT)
    # domain claimed
    name.update_status()
    assert not chain_fixture.NODE_CLI.AEName(domain).is_available(), 'The name should be claimed now'
    name.update_status()
    print("claimed name", name)
    print("pointers", name.pointers)
    assert len(name.pointers) > 0, 'Pointers should not be empty'
    assert name.pointers[0].id == chain_fixture.ACCOUNT.get_address()
    assert name.pointers[0].key == "account_pubkey"


# TODO: enable the test check for pointers

def test_name_transfer_ownership(chain_fixture, random_domain):
    name = chain_fixture.NODE_CLI.AEName(random_domain)
    name.full_claim_blocking(chain_fixture.ACCOUNT)
    assert name.status == AEName.Status.CLAIMED
    name.update_status()
    assert name.pointers[0].id == chain_fixture.ACCOUNT.get_address()
    assert name.pointers[0].key == "account_pubkey"

    # now transfer the name to the other account
    name.transfer_ownership(chain_fixture.ACCOUNT, chain_fixture.ACCOUNT_1.get_address())
    assert name.status == AEName.Status.TRANSFERRED
    # try changing the target using that new account
    name.update_status()
    name.update(chain_fixture.ACCOUNT_1, chain_fixture.ACCOUNT_1.get_address())
    name.update_status()
    assert len(name.pointers) > 0, 'Pointers should not be empty'
    assert name.pointers[0].id == chain_fixture.ACCOUNT_1.get_address()
    assert name.pointers[0].key == "account_pubkey"


def test_name_revocation(chain_fixture, random_domain):
    domain = random_domain
    name = chain_fixture.NODE_CLI.AEName(domain)
    name.full_claim_blocking(chain_fixture.ACCOUNT)
    name.revoke(chain_fixture.ACCOUNT)
    assert name.status == AEName.Status.REVOKED
    assert chain_fixture.NODE_CLI.AEName(domain).is_available()
