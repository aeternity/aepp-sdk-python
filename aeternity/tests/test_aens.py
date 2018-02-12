import random
import string

from pytest import raises

from aeternity import Config, EpochClient
from aeternity.aens import InvalidName, Name, AENSException
from aeternity.config import ConfigException

# to run this test in other environments set the env vars as specified in the
# config.py
try:
    # if there are no env vars set for the config, this call will fail
    Config()
except ConfigException:
    # in this case we create a default config that should work on the dev
    # machines.
    Config.set_default(Config(local_port=3013, internal_port=3113, websocket_port=3114))


def random_domain(length=10):
    rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return rand_str + '.aet'

def test_name_validation_fails():
    with raises(InvalidName):
        Name('test.lol')

def test_name_validation_succeeds():
    Name('test.aet')

def test_name_is_available():
    name = Name(random_domain())
    assert name.is_available()

def test_name_status_availavle():
    name = Name(random_domain())
    assert name.status == Name.Status.UNKNOWN
    name.update_status()
    assert name.status == Name.Status.AVAILABLE

def test_name_claim_lifecycle():
    domain = random_domain()
    name = Name(domain)
    assert name.status == Name.Status.UNKNOWN
    name.update_status()
    assert name.status == Name.Status.AVAILABLE
    name.preclaim()
    assert name.status == Name.Status.PRECLAIMED
    name.claim_blocking()
    assert name.status == Name.Status.CLAIMED

def test_name_status_unavailable():
    # claim a domain
    domain = random_domain()
    occupy_name = Name(domain)
    occupy_name.full_claim_blocking()
    # wait for the state to propagate in the block chain
    EpochClient().wait_for_next_block()
    same_name = Name(domain)
    assert not same_name.is_available()

def test_name_update():
    client = EpochClient()
    # claim a domain
    domain = random_domain()
    name = Name(domain)
    name.full_claim_blocking()
    name.update(target=client.get_pubkey())
    client.wait_for_next_block()
    name.update_status()
    assert name.pointers['account_pubkey'] == client.get_pubkey()

def test_transfer_ownership():
    client = EpochClient()
    name = Name(random_domain())
    name.full_claim_blocking()
    client.wait_for_next_block()
    name.transfer_ownership('ak$3scLu3oJbhsdCJkDjfJ6BUPJ4M9ZZJe57CQ56deSbEXhaTSfG3Wf3i2GYZV6APX7RDDVk4Weewb7oLePte3H3QdBw4rMZw')
    assert name.status == Name.Status.TRANSFERRED

def test_transfer_failure_wrong_pubkey():
    client = EpochClient()
    name = Name(random_domain())
    name.full_claim_blocking()
    client.wait_for_next_block()
    with raises(AENSException):
        name.transfer_ownership('ak$deadbeef')

def test_revocation():
    name = Name(random_domain())
    name.full_claim_blocking()
    EpochClient().wait_for_next_block()
    name.revoke()
    assert name.status == Name.Status.REVOKED
