import shutil
import subprocess
from subprocess import CalledProcessError

import os
import tempfile
from contextlib import contextmanager
import aeternity
from aeternity.epoch import EpochClient
from . import NODE_URL, NODE_URL_INTERNAL, KEYPAIR

import pytest

current_folder = os.path.dirname(os.path.abspath(__file__))
aecli_exe = os.path.join(current_folder, '..', '..', 'aecli')


def call_aecli(*params):
    args = [aecli_exe, '-u', NODE_URL, '-i', NODE_URL_INTERNAL] + list(params)
    output = subprocess.check_output(args).decode('ascii')
    return output.strip()


@contextmanager
def tempdir():
    # contextmanager to generate and delete a temporary directory
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def test_cli_version():
    version_str = call_aecli('--version')
    assert version_str == f"aecli, version {aeternity.__version__}"


def test_cli_balance():
    balance_str = call_aecli('--quiet', 'inspect', 'account',  KEYPAIR.get_address())
    assert balance_str.isnumeric()
    balance = int(balance_str)
    assert balance > 0


def test_cli_top():
    output = call_aecli('--quiet', 'chain', 'top')
    lines = output.split('\n')
    assert lines[0].startswith('bh$')  # block hash
    assert int(lines[1]) > 0  # block height
    assert lines[2].startswith('bs$')  # block state
    assert len(lines) == 7


def test_cli_generate_wallet():
    with tempdir() as tmp_path:
        wallet_key = os.path.join(tmp_path, 'key')
        call_aecli('wallet', wallet_key, 'create', '--password', 'secret', '--force')
        # make sure the folder contains the keys
        files = sorted(os.listdir(tmp_path))
        assert len(files) == 2
        assert files[0] == 'key'
        assert files[1] == 'key.pub'


def test_cli_generate_wallet_and_wallet_info():
    with tempdir() as tmp_path:
        wallet_path = os.path.join(tmp_path, 'key')
        output = call_aecli('--quiet', 'wallet', wallet_path, 'create', '--password', 'secret')
        gen_address = output.split('\n')[1]
        assert gen_address.startswith('ak$')
        read_address = call_aecli('--quiet', 'wallet', wallet_path, 'address', '--password', 'secret')
        assert read_address.startswith('ak$')
        assert read_address == gen_address


def test_cli_read_wallet_fail():

    with tempdir() as tmp_path:
        wallet_path = os.path.join(tmp_path, 'key')
        output = call_aecli('--quiet', 'wallet', wallet_path, 'create', '--password', 'secret')
        gen_address = output.split('\n')[1]
        try:
            read_address = call_aecli('--quiet', 'wallet', wallet_path, 'address', '--password', 'WRONGPASS')
            assert gen_address != read_address
        except CalledProcessError:
            # this is fine because invalid passwords exists the command with retcode 1
            pass


@pytest.mark.skip('Cannot spend using a waller without balance. We have to mine into that wallet somehow')
def test_cli_spend():
    with tempdir() as tmp_path:
        wallet_path = os.path.join(tmp_path, 'key')
        call_aecli('wallet', wallet_path, 'create',  '--password', 'whatever')
        receipient_address = call_aecli('-q', 'wallet', wallet_path, 'address',  '--password', 'whatever')
    with tempdir() as tmp_path:
        wallet_path = os.path.join(tmp_path, 'key')
        call_aecli('wallet', wallet_path, 'create', '--password', 'secret')
        output = call_aecli('wallet', wallet_path, 'spend', receipient_address, '1', '--password', 'secret')
        assert 'Transaction sent' in output


@pytest.mark.skip('We currently cannot verify if the transaction failed because of a wrong password or some other error '
                  '(e.g. no balance)')
def test_cli_spend_wrong_password():
    with tempdir() as wallet_path:
        output = call_aecli('generate', 'wallet', wallet_path, '--password', 'whatever')
        receipient_address = output.split('\n')[1][len('Address: '):]
    with tempdir() as wallet_path:
        call_aecli('generate', 'wallet', wallet_path, '--password', 'secret')
        output = call_aecli('spend', '1', receipient_address, wallet_path, '--password', 'WRONGPASS')
        assert 'Transaction sent' in output


def test_cli_spend_invalid_amount():
    # try to send a negative amount
    with tempdir() as tmp_path:
        wallet_path = os.path.join(tmp_path, 'key')
        output = call_aecli('--quiet', 'wallet', wallet_path, 'create', '--password', 'whatever')
        receipient_address = output.split('\n')[1]
    with tempdir() as tmp_path:
        wallet_path = os.path.join(tmp_path, 'key')
        output = call_aecli('--quiet', 'wallet', wallet_path, 'create', '--password', 'secret')
        with pytest.raises(subprocess.CalledProcessError):
            output = call_aecli('wallet', wallet_path, 'spend', receipient_address, '-1', '--password', 'secret')


def test_cli_inspect_block_by_height():
    height = EpochClient().get_height()
    output = call_aecli('--quiet', 'inspect', 'height', str(height))
    lines = output.split('\n')
    assert lines[0].startswith("bh$")
    assert lines[1] == str(height)


def test_cli_inspect_block_by_hash():
    height = EpochClient().get_height()
    output = call_aecli('--quiet', 'inspect', 'height', str(height))
    lines = output.split('\n')
    # retrieve the block hash
    block_hash = lines[0]
    output = call_aecli('--quiet', 'inspect', 'block', block_hash)
    blines = output.split('\n')
    assert lines[0] == blines[0]
    assert lines[1] == blines[1]
    assert lines[2] == blines[2]
    assert lines[3] == blines[3]


def test_cli_inspect_name():
    output = call_aecli('--quiet', 'inspect', 'name', 'whatever.aet')
    assert output == "AVAILABLE"


@pytest.mark.skip('NOT IMPLEMENTED YET')
def test_cli_inspect_block_by_latest():
    # TODO
    raise NotImplementedError()


@pytest.mark.skip('NOT IMPLEMENTED YET')
def test_cli_inspect_block_by_invalid_arg():
    # TODO
    raise NotImplementedError()


@pytest.mark.skip('NOT IMPLEMENTED YET')
def test_cli_inspect_transaction_by_hash():
    # TODO
    raise NotImplementedError()
