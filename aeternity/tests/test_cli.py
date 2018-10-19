import subprocess
from subprocess import CalledProcessError
import json
import os
import aeternity
import random
from aeternity.tests import NODE_URL, NODE_URL_DEBUG, ACCOUNT, EPOCH_CLI, tempdir, random_domain
from aeternity.signing import Account
from aeternity import utils
from aeternity.aens import AEName

import pytest

current_folder = os.path.dirname(os.path.abspath(__file__))
aecli_exe = os.path.join(current_folder, '..', '..', 'aecli')


@pytest.fixture
def account_path():
    with tempdir() as tmp_path:
        # save the private key on file
        sender_path = os.path.join(tmp_path, 'sender')
        ACCOUNT.save_to_keystore_file(sender_path, 'aeternity_bc')
        yield sender_path


def call_aecli(*params):
    args = [aecli_exe, '-u', NODE_URL, '-d', NODE_URL_DEBUG] + list(params) + ['--wait', '--json']
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


def test_cli_balance():
    j = call_aecli('inspect', ACCOUNT.get_address())
    assert isinstance(j.get("balance"), int)
    assert isinstance(j.get("nonce"), int)
    assert j.get("id") == ACCOUNT.get_address()
    assert j.get("balance") > 0


def test_cli_top():
    j = call_aecli('chain', 'top')
    assert j.get("hash").startswith('kh_') or j.get("hash").startswith('mh_')  # block hash


def test_cli_generate_account():
    with tempdir() as tmp_path:
        account_key = os.path.join(tmp_path, 'key')
        j = call_aecli('account', 'create', account_key, '--password', 'secret', '--overwrite')
        gen_address = j.get("Address")
        assert utils.is_valid_hash(gen_address, prefix='ak')
        # make sure the folder contains the keys
        files = sorted(os.listdir(tmp_path))
        assert len(files) == 1
        assert files[0].startswith("key")


def test_cli_generate_account_and_account_info():
    with tempdir() as tmp_path:
        account_path = os.path.join(tmp_path, 'key')
        j = call_aecli('account', 'create', account_path, '--password', 'secret')
        gen_address = j.get("Address")
        assert utils.is_valid_hash(gen_address, prefix='ak')
        j1 = call_aecli('account', 'address', account_path, '--password', 'secret')
        assert utils.is_valid_hash(j1.get('Address'), prefix='ak')


def test_cli_read_account_fail():
    with tempdir() as tmp_path:
        account_path = os.path.join(tmp_path, 'key')
        j = call_aecli('account', 'create', account_path, '--password', 'secret')
        try:
            j1 = call_aecli('account', 'address', account_path, '--password', 'WRONGPASS')
            assert j.get("Address") != j1.get("Address")
        except CalledProcessError:
            # this is fine because invalid passwords exists the command with retcode 1
            pass


# @pytest.mark.skip('Fails with account not founds only on the master build server')
def test_cli_spend(account_path):
    # generate a new address
    recipient_address = Account.generate().get_address()
    # call the cli
    call_aecli('account', 'spend', account_path, recipient_address, "90", '--password', 'aeternity_bc')
    # test that the recipient account has the requested amount
    print(f"recipient address is {recipient_address}")
    recipient_account = EPOCH_CLI.get_account_by_pubkey(pubkey=recipient_address)
    print(f"recipient address {recipient_address}, balance {recipient_account.balance}")
    assert recipient_account.balance == 90


def test_cli_spend_invalid_amount(account_path):
    with pytest.raises(subprocess.CalledProcessError):
        receipient_address = Account.generate().get_address()
        call_aecli('account', 'spend', account_path,  receipient_address, '-1', '--password', 'secret')


def test_cli_inspect_key_block_by_height():
    height = EPOCH_CLI.get_current_key_block_height()
    j = call_aecli('inspect', str(height))
    assert utils.is_valid_hash(j.get("hash"), prefix=["kh", "mh"])
    assert j.get("height") == height


def test_cli_inspect_key_block_by_hash():
    height = EPOCH_CLI.get_current_key_block_height()
    jh = call_aecli('inspect', str(height))
    # retrieve the block hash
    jb = call_aecli('inspect', jh.get("hash"))

    assert jh.get("height") == jb.get("height")
    assert jh.get("hash") == jb.get("hash")
    assert jh.get("time") == jb.get("time")
    assert jh.get("miner") == jb.get("miner")
    assert jh.get("nonce") == jb.get("nonce")


def test_cli_inspect_name():
    j = call_aecli('inspect', 'whatever.aet')
    assert j.get("Status") == "AVAILABLE"


def test_cli_inspect_transaction_by_hash():
    # fill the account from genesys
    na = Account.generate()
    amount = random.randint(50, 150)
    _, _, tx_hash = EPOCH_CLI.spend(ACCOUNT, na.get_address(), amount)
    # now inspect the transaction
    j = call_aecli('inspect', tx_hash)
    assert j.get("hash") == tx_hash
    assert j.get("block_height") > 0
    assert j.get("tx", {}).get("recipient_id") == na.get_address()
    assert j.get("tx", {}).get("sender_id") == ACCOUNT.get_address()
    assert j.get("tx", {}).get("amount") == amount


def test_cli_name_claim(account_path):
    # create a random domain
    domain = random_domain()
    print(f"Domain is {domain}")
    # call the cli
    call_aecli('name', 'claim', account_path, domain, '--password', 'aeternity_bc')
    EPOCH_CLI.AEName(domain).status == AEName.Status.CLAIMED
