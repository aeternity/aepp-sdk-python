from aeternity.aens import AEName
from aeternity.identifiers import PROTOCOL_LIMA
from tests.conftest import random_domain
from aeternity.signing import Account

from pytest import raises, skip


def test_name_validation_fails(chain_fixture):
    with raises(ValueError):
        chain_fixture.NODE_CLI.AEName('test.lol')
    chain_fixture.NODE_CLI.AEName('test.aet')
    chain_fixture.NODE_CLI.AEName('test.test')


def test_name_validation_succeeds(chain_fixture):
    chain_fixture.NODE_CLI.AEName('test.test')
    chain_fixture.NODE_CLI.AEName('test.aet')


def test_name_is_available(chain_fixture):
    domain = random_domain(tld='aet' if chain_fixture.NODE_CLI.get_consensus_protocol_version() >= PROTOCOL_LIMA else 'test')
    name = chain_fixture.NODE_CLI.AEName(domain)
    assert name.is_available()


def test_name_status_available(chain_fixture):
    domain = random_domain(length=13 ,tld='aet' if chain_fixture.NODE_CLI.get_consensus_protocol_version() >= PROTOCOL_LIMA else 'test')
    name = chain_fixture.NODE_CLI.AEName(domain)
    assert name.status == AEName.Status.UNKNOWN
    name.update_status()
    assert name.status == AEName.Status.AVAILABLE


def test_name_claim_lifecycle(chain_fixture):
    try:
        # avoid auctions
        domain = random_domain(length=13 ,tld='aet' if chain_fixture.NODE_CLI.get_consensus_protocol_version() >= PROTOCOL_LIMA else 'test')
        node_cli = chain_fixture.NODE_CLI
        name = node_cli.AEName(domain)
        assert name.status == AEName.Status.UNKNOWN
        name.update_status()
        assert name.status == AEName.Status.AVAILABLE
        preclaim = name.preclaim(chain_fixture.ALICE)
        assert name.status == AEName.Status.PRECLAIMED
        node_cli.wait_for_confirmation(preclaim.hash)
        name.claim(preclaim.hash, chain_fixture.ALICE, preclaim.metadata.salt)
        assert name.status == AEName.Status.CLAIMED
    except Exception as e:
        print(e)
        assert e is None

def test_name_auction(chain_fixture):
    if chain_fixture.NODE_CLI.get_consensus_protocol_version() < PROTOCOL_LIMA:
        skip("name auction is only supported after Lima HF")
        return
    try:
        domain = random_domain(length=12)
        node_cli = chain_fixture.NODE_CLI
        name = node_cli.AEName(domain)
        assert name.status == AEName.Status.UNKNOWN
        name.update_status()
        assert name.status == AEName.Status.AVAILABLE
        preclaim = name.preclaim(chain_fixture.ALICE)
        assert name.status == AEName.Status.PRECLAIMED
        node_cli.wait_for_confirmation(preclaim.hash)
        claim_tx = name.claim(preclaim.hash, chain_fixture.ALICE, preclaim.metadata.salt)
        print(claim_tx)
        assert name.status == AEName.Status.CLAIMED
        # bob will make another bid
        name2 = node_cli.AEName(domain)
        bid = AEName.compute_bid_fee(domain)
        bid_tx = name2.bid(chain_fixture.BOB, bid)
        print("BID TX", bid_tx)
        # get the tx height
        bid_h = node_cli.wait_for_transaction(bid_tx.hash)
        print(f"BOB BID Height is  {bid_h}")
        # now we should wait to see that bob gets the name
        bid_ends = AEName.compute_auction_end_block(domain, bid_h)
        # 
        print(f"BID STARTED AT {bid_h} WILL END AT {bid_ends}")
    except Exception as e:
        print(e)
        assert e is None


def test_name_status_unavailable(chain_fixture):
    # avoid auctions
    domain = random_domain(length=13 ,tld='aet' if chain_fixture.NODE_CLI.get_consensus_protocol_version() >= PROTOCOL_LIMA else 'test')
    print(f"domain is {domain}")
    occupy_name = chain_fixture.NODE_CLI.AEName(domain)
    occupy_name.full_claim_blocking(chain_fixture.ALICE)
    # try to get the same name
    same_name = chain_fixture.NODE_CLI.AEName(domain)
    assert not same_name.is_available()


def test_name_update(chain_fixture):
    # avoid auctions
    domain = random_domain(length=13 ,tld='aet' if chain_fixture.NODE_CLI.get_consensus_protocol_version() >= PROTOCOL_LIMA else 'test')
    print(f"domain is {domain}")
    name = chain_fixture.NODE_CLI.AEName(domain)
    print("Claim name ", domain)
    name.full_claim_blocking(chain_fixture.ALICE)
    # domain claimed
    name.update_status()
    assert not chain_fixture.NODE_CLI.AEName(domain).is_available(), 'The name should be claimed now'
    name.update_status()
    print("claimed name", name)
    print("pointers", name.pointers)
    assert len(name.pointers) > 0, 'Pointers should not be empty'
    assert name.pointers[0].id == chain_fixture.ALICE.get_address()
    assert name.pointers[0].key == "account_pubkey"

def test_spend_by_name(chain_fixture, random_domain):
    # claim a domain
    domain = random_domain
    print(f"domain is {domain}")
    name = chain_fixture.NODE_CLI.AEName(domain)
    print("Claim name ", domain)
    # generate a new address
    target_address = Account.generate().get_address()
    print(f"Target address {target_address}")
    name.full_claim_blocking(chain_fixture.ACCOUNT, target=target_address)
    # domain claimed
    name.update_status()
    assert not chain_fixture.NODE_CLI.AEName(domain).is_available(), 'The name should be claimed now'
    name.update_status()
    print(f"domain is {name.domain} name_hash {name.name_hash}")
    print("pointers", name.pointers)
    tx = chain_fixture.NODE_CLI.spend_by_name(chain_fixture.ACCOUNT, domain, 100)
    print("DATA ", tx)
    recipient_account = chain_fixture.NODE_CLI.get_account_by_pubkey(pubkey=target_address)
    print(f"recipient address {target_address}, balance {recipient_account.balance}")
    assert recipient_account.balance == 100

# TODO: enable the test check for pointers

def test_name_transfer_ownership(chain_fixture):
    # avoid auctions
    domain = random_domain(length=13 ,tld='aet' if chain_fixture.NODE_CLI.get_consensus_protocol_version() >= PROTOCOL_LIMA else 'test')
    name = chain_fixture.NODE_CLI.AEName(domain)
    name.full_claim_blocking(chain_fixture.ALICE)
    assert name.status == AEName.Status.CLAIMED
    name.update_status()
    assert name.pointers[0].id == chain_fixture.ALICE.get_address()
    assert name.pointers[0].key == "account_pubkey"

    # now transfer the name to the other account
    name.transfer_ownership(chain_fixture.ALICE, chain_fixture.BOB.get_address())
    assert name.status == AEName.Status.TRANSFERRED
    # try changing the target using that new account
    name.update_status()
    name.update(chain_fixture.BOB, chain_fixture.BOB.get_address())
    name.update_status()
    assert len(name.pointers) > 0, 'Pointers should not be empty'
    assert name.pointers[0].id == chain_fixture.BOB.get_address()
    assert name.pointers[0].key == "account_pubkey"


def test_name_revocation(chain_fixture):
    # avoid auctions
    domain = random_domain(length=13 ,tld='aet' if chain_fixture.NODE_CLI.get_consensus_protocol_version() >= PROTOCOL_LIMA else 'test')
    name = chain_fixture.NODE_CLI.AEName(domain)
    name.full_claim_blocking(chain_fixture.ALICE)
    name.revoke(chain_fixture.ALICE)
    assert name.status == AEName.Status.REVOKED
    assert chain_fixture.NODE_CLI.AEName(domain).is_available()
