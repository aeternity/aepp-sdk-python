import subprocess
from subprocess import CalledProcessError
import json
import os
import aeternity
import random
from tests.conftest import NODE_URL, NODE_URL_DEBUG, NETWORK_ID
from aeternity.signing import Account
from aeternity import utils
from aeternity.aens import AEName

import pytest

current_folder = os.path.dirname(os.path.abspath(__file__))
aecli_exe = os.path.join(current_folder, '..', 'aecli')


def _account_path(tempdir, account):
    # save the private key on file
    sender_path = os.path.join(tempdir, 'sender')
    account.save_to_keystore_file(sender_path, 'aeternity_bc')
    return sender_path


def call_aecli(*params):
    args = [aecli_exe, '-u', NODE_URL, '-d', NODE_URL_DEBUG] + list(params) + ['--json']
    cmd = " ".join(args)
    print(cmd)
    status, output = subprocess.getstatusoutput(cmd)
    if status != 0:
        print(output)
        raise subprocess.CalledProcessError(status, cmd)
    try:
        return json.loads(output)
    except Exception as e:
        return output


def test_cli_version():
    v = call_aecli('--version')
    print(v, aeternity.__version__)
    assert v == f"aecli, version {aeternity.__version__}"


def test_cli_balance(chain_fixture):
    j = call_aecli('inspect', chain_fixture.ACCOUNT.get_address())
    assert isinstance(j.get("balance"), int)
    assert isinstance(j.get("nonce"), int)
    assert j.get("id") == chain_fixture.ACCOUNT.get_address()
    assert j.get("balance") > 0


def test_cli_top():
    j = call_aecli('chain', 'top')
    assert j.get("hash").startswith('kh_') or j.get("hash").startswith('mh_')  # block hash


def test_cli_generate_account(tempdir):
    account_key = os.path.join(tempdir, 'key')
    j = call_aecli('account', 'create', account_key, '--password', 'secret', '--overwrite')
    gen_address = j.get("Address")
    assert utils.is_valid_hash(gen_address, prefix='ak')
    # make sure the folder contains the keys
    files = sorted(os.listdir(tempdir))
    assert len(files) == 1
    assert files[0].startswith("key")


def test_cli_generate_account_and_account_info(tempdir):
    account_path = os.path.join(tempdir, 'key')
    j = call_aecli('account', 'create', account_path, '--password', 'secret')
    gen_address = j.get("Address")
    assert utils.is_valid_hash(gen_address, prefix='ak')
    j1 = call_aecli('account', 'address', account_path, '--password', 'secret')
    assert utils.is_valid_hash(j1.get('Address'), prefix='ak')


def test_cli_read_account_fail(tempdir):
    account_path = os.path.join(tempdir, 'key')
    j = call_aecli('account', 'create', account_path, '--password', 'secret')
    try:
        j1 = call_aecli('account', 'address', account_path, '--password', 'WRONGPASS')
        assert j.get("Address") != j1.get("Address")
    except CalledProcessError:
        # this is fine because invalid passwords exists the command with retcode 1
        pass


# @pytest.mark.skip('Fails with account not founds only on the master build server')
def test_cli_spend(chain_fixture, tempdir):
    account_path = _account_path(tempdir, chain_fixture.ACCOUNT)
    # generate a new address
    recipient_address = Account.generate().get_address()
    # call the cli
    call_aecli('account', 'spend', account_path, recipient_address, "90", '--password', 'aeternity_bc', '--network-id', NETWORK_ID, '--wait')
    # test that the recipient account has the requested amount
    print(f"recipient address is {recipient_address}")
    recipient_account = chain_fixture.NODE_CLI.get_account_by_pubkey(pubkey=recipient_address)
    print(f"recipient address {recipient_address}, balance {recipient_account.balance}")
    assert recipient_account.balance == 90


def test_cli_spend_invalid_amount(chain_fixture, tempdir):
    with pytest.raises(subprocess.CalledProcessError):
        account_path = _account_path(tempdir, chain_fixture.ACCOUNT)
        receipient_address = Account.generate().get_address()
        call_aecli('account', 'spend', account_path,  receipient_address, '-1', '--password', 'secret')


def test_cli_inspect_key_block_by_height(chain_fixture):
    height = chain_fixture.NODE_CLI.get_current_key_block_height()
    j = call_aecli('inspect', str(height))
    assert utils.is_valid_hash(j.get("hash"), prefix=["kh", "mh"])
    assert j.get("height") == height


def test_cli_inspect_key_block_by_hash(chain_fixture):
    height = chain_fixture.NODE_CLI.get_current_key_block_height()
    jh = call_aecli('inspect', str(height))
    # retrieve the block hash
    jb = call_aecli('inspect', jh.get("hash"))

    assert jh.get("height") == jb.get("height")
    assert jh.get("hash") == jb.get("hash")
    assert jh.get("time") == jb.get("time")
    assert jh.get("miner") == jb.get("miner")
    assert jh.get("nonce") == jb.get("nonce")


def test_cli_inspect_name():
    j = call_aecli('inspect', 'whatever.test')
    assert "name not found" in j.get("message", "").lower()


def test_cli_inspect_transaction_by_hash(chain_fixture):
    # fill the account from genesys
    na = Account.generate()
    amount = random.randint(50, 150)
    tx = chain_fixture.NODE_CLI.spend(chain_fixture.ACCOUNT, na.get_address(), amount)
    # now inspect the transaction
    j = call_aecli('inspect', tx.hash)
    assert j.get("hash") == tx.hash
    assert j.get("block_height") > 0
    assert j.get("tx", {}).get("recipient_id") == na.get_address()
    assert j.get("tx", {}).get("sender_id") == chain_fixture.ACCOUNT.get_address()
    assert j.get("tx", {}).get("amount") == amount


@pytest.mark.skip("Name claim is outdated")
def test_cli_name_claim(account_path, chain_fixture, random_domain):
    # create a random domain
    domain = random_domain()
    print(f"Domain is {domain}")
    # call the cli
    call_aecli('name', 'claim', account_path, domain, '--password', 'aeternity_bc', '--network-id', NETWORK_ID)
    chain_fixture.NODE_CLI.AEName(domain).status == AEName.Status.CLAIMED


def test_cli_phases_spend(chain_fixture, tempdir):
    account_path = _account_path(tempdir, chain_fixture.ACCOUNT)
    # generate a new address
    recipient_id = Account.generate().get_address()
    # step one, generate transaction
    nonce = chain_fixture.NODE_CLI.get_account_by_pubkey(pubkey=chain_fixture.ACCOUNT.get_address()).nonce + 1
    j = call_aecli('tx', 'spend', chain_fixture.ACCOUNT.get_address(), recipient_id, '100', '--nonce', f'{nonce}')
    # assert chain_fixture.ACCOUNT.get_address == j.get("Sender account")
    assert recipient_id == j.get("data", {}).get("recipient_id")
    # step 2, sign the transaction
    tx_unsigned = j.get("tx")
    s = call_aecli('account', 'sign', account_path, tx_unsigned, '--password', 'aeternity_bc', '--network-id', NETWORK_ID)
    tx_signed = s.get("tx")
    # recipient_account = chain_fixture.NODE_CLI.get_account_by_pubkey(pubkey=recipient_id)
    # assert recipient_account.balance == 0
    # step 3 broadcast
    call_aecli('tx', 'broadcast', tx_signed, "--wait")
    # b.get("Transaction hash")
    # verify
    recipient_account = chain_fixture.NODE_CLI.get_account_by_pubkey(pubkey=recipient_id)
    assert recipient_account.balance == 100
