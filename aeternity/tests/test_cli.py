import subprocess
from subprocess import CalledProcessError
import json
import os
import aeternity
import random
from aeternity.tests import NODE_URL, KEYPAIR, EPOCH_CLI, tempdir
from aeternity.signing import Account
from aeternity import utils

import pytest

current_folder = os.path.dirname(os.path.abspath(__file__))
aecli_exe = os.path.join(current_folder, '..', '..', 'aecli')


def call_aecli(*params):
    args = [aecli_exe, '-u', NODE_URL, '--wait', '--json'] + list(params)
    print(" ".join(args))
    output = subprocess.check_output(args).decode('ascii')
    o = output.strip()
    try:
        return json.loads(o)
    except Exception as e:
        return o


def test_cli_version():
    v = call_aecli('--version')
    print(v, aeternity.__version__)
    assert v == f"aecli, version {aeternity.__version__}"


def test_cli_balance():
    j = call_aecli('inspect', KEYPAIR.get_address())
    assert isinstance(j.get("balance"), int)
    assert isinstance(j.get("nonce"), int)
    assert j.get("id") == KEYPAIR.get_address()
    assert j.get("balance") > 0


def test_cli_top():
    j = call_aecli('chain', 'top')
    assert j.get("hash").startswith('kh_') or j.get("hash").startswith('mh_')  # block hash


def test_cli_generate_account():
    with tempdir() as tmp_path:
        account_key = os.path.join(tmp_path, 'key')
        call_aecli('account', account_key, 'create', '--password', 'secret', '--force')
        # make sure the folder contains the keys
        files = sorted(os.listdir(tmp_path))
        assert len(files) == 1
        assert files[0].startswith("key")


def test_cli_generate_account_and_account_info():
    with tempdir() as tmp_path:
        account_path = os.path.join(tmp_path, 'key')
        j = call_aecli('account', account_path, 'create', '--password', 'secret')
        gen_address = j.get("Account address")
        assert utils.is_valid_hash(gen_address, prefix='ak')
        j1 = call_aecli('account', account_path, 'address', '--password', 'secret')
        assert utils.is_valid_hash(j1.get('Account address'), prefix='ak')


def test_cli_read_account_fail():
    with tempdir() as tmp_path:
        account_path = os.path.join(tmp_path, 'key')
        j = call_aecli('account', account_path, 'create', '--password', 'secret')
        try:
            j1 = call_aecli('account', account_path, 'address', '--password', 'WRONGPASS')
            assert j.get("Account address") != j1.get("Account address")
        except CalledProcessError:
            # this is fine because invalid passwords exists the command with retcode 1
            pass


@pytest.mark.skip('Fails with account not founds only on the master build server')
def test_cli_spend():
    with tempdir() as tmp_path:
        # save the private key on file
        sender_path = os.path.join(tmp_path, 'sender')
        call_aecli('account', sender_path, 'save', KEYPAIR.get_private_key(), '--password', 'whatever')
        # generate a new address
        recipient_address = Account.generate().get_address()
        # call the cli
        call_aecli('account', sender_path, 'spend', '--password', 'whatever', recipient_address, "90")
        # test that the recipient account has the requested amount
        print(f"recipient address is {recipient_address}")
        recipient_account = EPOCH_CLI.get_account_by_pubkey(pubkey=recipient_address)
        assert recipient_account.balance == 90


def test_cli_spend_invalid_amount():
    # try to send a negative amount
    with tempdir() as tmp_path:
        account_path = os.path.join(tmp_path, 'key')
        j = call_aecli('account', account_path, 'create', '--password', 'whatever')
        receipient_address = j.get("Account address")
    with tempdir() as tmp_path:
        account_path = os.path.join(tmp_path, 'key')
        call_aecli('account', account_path, 'create', '--password', 'secret')
        with pytest.raises(subprocess.CalledProcessError):
            call_aecli('account', account_path, 'spend', receipient_address, '-1', '--password', 'secret')


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
    _, _, tx_hash = EPOCH_CLI.spend(KEYPAIR, na.get_address(), amount)
    # now inspect the transaction
    j = call_aecli('inspect', tx_hash)
    assert j.get("hash") == tx_hash
    assert j.get("block_height") > 0
    assert j.get("tx", {}).get("recipient_id") == na.get_address()
    assert j.get("tx", {}).get("sender_id") == KEYPAIR.get_address()
    assert j.get("tx", {}).get("amount") == amount
