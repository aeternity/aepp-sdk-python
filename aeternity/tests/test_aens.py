import random
import string

import pytest
from pytest import raises, skip

from aeternity import Config, EpochClient
from aeternity.aens import AEName, AENSException
from aeternity.config import ConfigException

# to run this test in other environments set the env vars as specified in the
# config.py
from aeternity.formatter import pretty_block
from aeternity.signing import KeyPair

try:
    # if there are no env vars set for the config, this call will fail
    Config()
except ConfigException:
    # in this case we create a default config that should work on the dev
    # machines.
    Config.set_defaults(Config(external_host=3013, internal_host=3113, websocket_host=3114))


keypair = KeyPair.read_from_dir('/home/tom/data/aeternity/epoch/_build/dev1/rel/epoch/data/aecore/keys/', 'secret')

def random_domain(length=10):
    rand_str = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    return rand_str + '.aet'

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
    occupy_name.full_claim_blocking(keypair)
    # wait for the state to propagate in the block chain
    EpochClient().wait_for_next_block()
    same_name = AEName(domain)
    assert not same_name.is_available()

def test_name_update():
    client = EpochClient()
    # claim a domain
    domain = random_domain()
    name = AEName(domain)
    name.full_claim_blocking(keypair)
    client.wait_for_next_block()
    assert not AEName(domain).is_available(), 'The name should be claimed now'
    name.update_status()
    transaction = name.update(keypair, target=client.get_pubkey())
    client.wait_for_next_block()
    name.update_status()
    assert name.pointers != [], 'Pointers should not be empty'
    assert name.pointers['account_pubkey'] == client.get_pubkey()

@pytest.mark.skip('The name transfer must be rewritten to use offline signing')
def test_transfer_ownership():
    client = EpochClient()
    domain = random_domain()
    name = AEName()
    name.full_claim_blocking(keypair)
    client.wait_for_next_block()
    name.update_status()
    assert name.status == AEName.Status.CLAIMED

    new_key_pair = KeyPair.generate()
    name.transfer_ownership(new_key_pair.get_address())

    assert name.status == AEName.Status.TRANSFERRED
    client.wait_for_next_block()
    # try changing the target using that new keypair
    name.update(new_key_pair, target=keypair.get_address())
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

@pytest.mark.skip('The revocation does not work like this. The revoked name will be only'
      'free after a certain amount of blocks, but this is not decided yet '
      'AFAIK -- tom 2018-02-28')
def test_revocation():
    domain = random_domain()
    name = AEName(domain)
    name.full_claim_blocking(keypair)
    EpochClient().wait_for_next_block()
    name.revoke()
    assert name.status == AEName.Status.REVOKED
    EpochClient().wait_for_next_block()
    assert AEName(domain).is_available()
