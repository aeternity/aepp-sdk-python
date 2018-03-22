import shutil
import subprocess

import os
import tempfile
from contextlib import contextmanager

current_folder = os.path.dirname(os.path.abspath(__file__))
aecli_exe = os.path.join(current_folder, '..', '..', 'aecli')


def call_aecli(*params):
    args = [aecli_exe] + list(params)
    output = subprocess.check_output(args).decode('ascii')
    return output.strip()


@contextmanager
def tempdir():
    try:
        path = tempfile.mkdtemp()
        yield path
    finally:
        shutil.rmtree(path)



def test_balance():
    balance_str = call_aecli('balance')
    assert balance_str.isnumeric()
    balance = int(balance_str)
    assert balance > 0


def test_height():
    balance_str = call_aecli('height')
    assert balance_str.isnumeric()
    balance = int(balance_str)
    assert balance > 0


def test_generate_wallet():
    with tempdir() as tmp_path:
        output = call_aecli('generate', 'wallet', tmp_path, '--password', 'secret')
        lines = output.split('\n')
        assert lines[0] == 'Your wallet has been generated:'
        assert lines[1].startswith('Address: ak$')
        assert lines[2].startswith('Saved to: ')
        # make sure the folder contains the keys
        files = sorted(os.listdir(tmp_path))
        assert len(files) == 2
        assert files[0] == 'key'
        assert files[1] == 'key.pub'


def test_generate_wallet_and_wallet_info():
    with tempdir() as tmp_path:
        output = call_aecli('generate', 'wallet', tmp_path, '--password', 'secret')
        gen_address_line = output.split('\n')[1]
        assert gen_address_line.startswith('Address: ')
        gen_address = gen_address_line[len('Address: '):]
        assert gen_address.startswith('ak$')
        output = call_aecli('wallet', 'info', tmp_path, '--password', 'secret')
        assert output.startswith('Address: ')
        read_address = output[len('Address: '):]
        assert read_address == gen_address

def test_read_wallet_fail():
    with tempdir() as tmp_path:
        output = call_aecli('generate', 'wallet', tmp_path, '--password', 'secret')
        gen_address = output.split('\n')[1][len('Address: '):]
        output = call_aecli('wallet', 'info', tmp_path, '--password', 'WRONGPASS')
        read_address = output[len('Address: '):]
        #TODO I guess this should fail more spectacularly. Just getting "another"
        #TODO wallet is a really subtle error state...
        assert gen_address != read_address

