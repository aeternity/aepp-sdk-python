import subprocess
from subprocess import CalledProcessError
import json
import os
import aeternity
import random
from tests.conftest import NODE_URL, NODE_URL_DEBUG, NETWORK_ID, random_domain
from aeternity import utils, identifiers
from aeternity.signing import Account
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
        print(f"CMD status {status}, output: {output}")
        raise subprocess.CalledProcessError(status, cmd)
    try:
        print(f"CMD status {status}, output: {output}")
        return json.loads(output)
    except Exception as e:
        return output


def test_cli_balance(chain_fixture):
    j = call_aecli('inspect', chain_fixture.ALICE.get_address())
    assert isinstance(j.get("balance"), int)
    assert isinstance(j.get("nonce"), int)
    assert j.get("id") == chain_fixture.ALICE.get_address()
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


def test_cli_spend(chain_fixture, tempdir):
    account_path = _account_path(tempdir, chain_fixture.ALICE)
    # generate a new address
    recipient_address = Account.generate().get_address()
    # call the cli
    call_aecli('account', 'spend', account_path, recipient_address, "90", '--password', 'aeternity_bc', '--wait')
    # test that the recipient account has the requested amount
    print(f"recipient address is {recipient_address}")
    recipient_account = chain_fixture.NODE_CLI.get_account_by_pubkey(pubkey=recipient_address)
    print(f"recipient address {recipient_address}, balance {recipient_account.balance}")
    assert recipient_account.balance == 90

def test_cli_spend_by_name(chain_fixture, tempdir):
    account_alice_path = _account_path(tempdir, chain_fixture.ALICE)
    # generate a new address
    recipient_address = Account.generate().get_address()
    domain = __fullclaim_domain(chain_fixture, tempdir, recipient_address)
    call_aecli('account', 'spend', account_alice_path, domain, "90", '--password', 'aeternity_bc', '--wait')
    # test that the recipient account has the requested amount
    print(f"recipient domain is {domain}")
    recipient_account = chain_fixture.NODE_CLI.get_account_by_pubkey(pubkey=recipient_address)
    print(f"recipient address {recipient_address}, balance {recipient_account.balance}")
    assert recipient_account.balance == 90

def test_cli_transfer_by_name(chain_fixture, tempdir):
    account_alice_path = _account_path(tempdir, chain_fixture.ALICE)
    # generate a new address
    recipient_address = Account.generate().get_address()
    domain = __fullclaim_domain(chain_fixture, tempdir, recipient_address)
    val = call_aecli('account', 'transfer', account_alice_path, domain, "0.01", '--password', 'aeternity_bc', '--wait')
    # test that the recipient account has the requested amount
    print(f"recipient domain is {domain}")
    recipient_account = chain_fixture.NODE_CLI.get_account_by_pubkey(pubkey=recipient_address)
    print(f"recipient address {recipient_address}, balance {recipient_account.balance}")
    assert recipient_account.balance == val['data']['tx']['data']['amount']

def test_cli_spend_invalid_amount(chain_fixture, tempdir):
    with pytest.raises(subprocess.CalledProcessError):
        account_path = _account_path(tempdir, chain_fixture.ALICE)
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
    amount = random.randint(1, 1000000000000000000)
    tx = chain_fixture.NODE_CLI.spend(chain_fixture.ALICE, na.get_address(), amount)
    # now inspect the transaction
    j = call_aecli('inspect', tx.hash)
    assert j.get("hash") == tx.hash
    assert j.get("data", {}).get("block_height") > 0
    assert j.get("data", {}).get("tx", {}).get("data", {}).get("recipient_id") == na.get_address()
    assert j.get("data", {}).get("tx", {}).get("data", {}).get("sender_id") == chain_fixture.ALICE.get_address()
    assert j.get("data", {}).get("tx", {}).get("data", {}).get("amount") == amount


def test_cli_phases_spend(chain_fixture, tempdir):
    account_path = _account_path(tempdir, chain_fixture.ALICE)
    # generate a new address
    recipient_id = Account.generate().get_address()
    # step one, generate transaction
    nonce = chain_fixture.NODE_CLI.get_account_by_pubkey(pubkey=chain_fixture.ALICE.get_address()).nonce + 1
    j = call_aecli('tx', 'spend', chain_fixture.ALICE.get_address(), recipient_id, '100', '--nonce', f'{nonce}')
    # assert chain_fixture.ALICE.get_address == j.get("Sender account")
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

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.skip("Have to suppress the test for a false positive due ci input")
def test_cli_name_claim(chain_fixture, tempdir):
    account_alice_path = _account_path(tempdir, chain_fixture.ALICE)
    # get a domain that is not under auction scheme
    domain = random_domain(length=13 ,tld='chain' if chain_fixture.NODE_CLI.get_consensus_protocol_version() >= identifiers.PROTOCOL_LIMA else 'test')
    # let alice preclaim a name 
    j = call_aecli('name', 'pre-claim', '--password', 'aeternity_bc', account_alice_path, domain, '--wait')
    # retrieve the salt and the transaction hash 
    salt = j.get("metadata",{}).get("salt")
    preclaim_hash = j.get("hash")
    # test that they are what we expect to be
    assert(isinstance(salt, int))
    assert(salt > 0)
    assert(utils.is_valid_hash(preclaim_hash, identifiers.TRANSACTION_HASH))
    # wait for confirmation
    chain_fixture.NODE_CLI.wait_for_confirmation(preclaim_hash)
    # now run the claim
    j = call_aecli('name', 'claim', account_alice_path, domain, '--password', 'aeternity_bc', '--name-salt', f"{salt}", '--preclaim-tx-hash', preclaim_hash, '--wait')
    assert(utils.is_valid_hash(j.get("hash"), identifiers.TRANSACTION_HASH))
    # now run the name update
    j = call_aecli('name', 'update', '--password', 'aeternity_bc', account_alice_path, domain, chain_fixture.ALICE.get_address())
    assert(utils.is_valid_hash(j.get("hash"), identifiers.TRANSACTION_HASH))
    # now inspect the name
    j = call_aecli('inspect', domain)
    pointers = j.get('pointers',[])
    assert(len(pointers) == 1)
    assert(pointers[0]['id'] == chain_fixture.ALICE.get_address())


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_cli_name_auction(chain_fixture, tempdir):
    if chain_fixture.NODE_CLI.get_consensus_protocol_version() < identifiers.PROTOCOL_LIMA:
        pytest.skip("name auction is only supported after Lima HF")
        return
    node_cli = chain_fixture.NODE_CLI
    account_alice_path = _account_path(tempdir, chain_fixture.ALICE)
    account_bob_path = _account_path(tempdir, chain_fixture.BOB)
    # get a domain that is under auction scheme
    domain = random_domain(length=9 ,tld='chain' if chain_fixture.NODE_CLI.get_consensus_protocol_version() >= identifiers.PROTOCOL_LIMA else 'test')
    # let alice preclaim a name 
    j = call_aecli('name', 'pre-claim', '--password', 'aeternity_bc', account_alice_path, domain, '--wait')
    # retrieve the salt and the transaction hash 
    salt = j.get("metadata",{}).get("salt")
    preclaim_hash = j.get("hash")
    # test that they are what we expect to be
    assert(isinstance(salt, int))
    assert(salt > 0)
    assert(utils.is_valid_hash(preclaim_hash, identifiers.TRANSACTION_HASH))
    # wait for confirmation
    chain_fixture.NODE_CLI.wait_for_confirmation(preclaim_hash)
    # now run the claim
    j = call_aecli('name', 'claim', account_alice_path, domain, '--password', 'aeternity_bc', '--name-salt', f"{salt}", '--preclaim-tx-hash', preclaim_hash, '--wait')
    assert(utils.is_valid_hash(j.get("hash"), identifiers.TRANSACTION_HASH))
    # check that the tx was mined
    claim_height = chain_fixture.NODE_CLI.get_transaction_by_hash(hash=j.get('hash')).block_height
    assert(isinstance(claim_height, int) and claim_height > 0)
    # now we have a first claim
    # this is the name fee and the end block
    name_fee = AEName.compute_bid_fee(domain)
    aucion_end = AEName.compute_auction_end_block(domain, claim_height)
    print(f"Name {domain}, name_fee {name_fee}, claim height: {claim_height}, auction_end: {aucion_end}")
    # now make another bid 
    # first compute the new name fee
    name_fee = AEName.compute_bid_fee(domain, name_fee)
    j = call_aecli('name', 'bid', account_bob_path, domain, f'{name_fee}', '--password', 'aeternity_bc', '--wait')
    assert(utils.is_valid_hash(j.get("hash"), identifiers.TRANSACTION_HASH))
    # check that the tx was mined
    claim_height = chain_fixture.NODE_CLI.get_transaction_by_hash(hash=j.get('hash')).block_height
    assert(isinstance(claim_height, int) and claim_height > 0)
    aucion_end = AEName.compute_auction_end_block(domain, claim_height)
    print(f"Name {domain}, name_fee {name_fee}, claim height: {claim_height}, auction_end: {aucion_end}")
    name = chain_fixture.NODE_CLI.AEName(domain)
    # name should still be available
    assert(name.is_available())

def test_cli_contract_deploy_call(chain_fixture, compiler_fixture, tempdir):
    node_cli = chain_fixture.NODE_CLI
    account_alice_path = _account_path(tempdir, chain_fixture.ALICE)
    # the contract
    c_src = "contract Identity =\n  entrypoint main(x : int) = x"
    c_deploy_function = "init"
    c_call_function = "main"
    c_call_function_param = 42
    # compile the contract
    compiler = compiler_fixture.COMPILER
    # compile and encode calldatas
    c_bin = compiler.compile(c_src).bytecode
    c_init_calldata = compiler.encode_calldata(c_src, c_deploy_function).calldata
    c_call_calldata = compiler.encode_calldata(c_src, c_call_function, c_call_function_param).calldata
    # write the contract to a file and execute the command
    contract_bin_path = os.path.join(tempdir, 'contract.bin')
    with open(contract_bin_path, "w") as fp:
        fp.write(c_bin)
    # deploy the contract
    j = call_aecli("contract", "deploy", "--wait" , "--password", "aeternity_bc", account_alice_path, contract_bin_path, "--calldata", c_init_calldata)
    c_id = j.get("metadata", {}).get("contract_id")
    assert utils.is_valid_hash(c_id, prefix=identifiers.CONTRACT_ID)
    # now call
    j = call_aecli("contract", "call", "--wait" , "--password", "aeternity_bc", account_alice_path, c_id, c_call_function, "--calldata", c_call_calldata)
    th = j.get("hash")
    assert utils.is_valid_hash(th, prefix=identifiers.TRANSACTION_HASH)

def __fullclaim_domain(chain_fixture, tempdir, recipient_address):
    account_path = _account_path(tempdir, chain_fixture.ALICE)
    domain = random_domain(length=13 ,tld='chain' if chain_fixture.NODE_CLI.get_consensus_protocol_version() >= identifiers.PROTOCOL_LIMA else 'test')
    # let alice preclaim a name 
    j = call_aecli('name', 'pre-claim', '--password', 'aeternity_bc', account_path, domain, '--wait')
    # retrieve the salt and the transaction hash 
    salt = j.get("metadata",{}).get("salt")
    preclaim_hash = j.get("hash")
    # wait for confirmation
    chain_fixture.NODE_CLI.wait_for_confirmation(preclaim_hash)
    # now run the claim
    j = call_aecli('name', 'claim', account_path, domain, '--password', 'aeternity_bc', '--name-salt', f"{salt}", '--preclaim-tx-hash', preclaim_hash, '--wait')
    # now run the name update
    j = call_aecli('name', 'update', '--password', 'aeternity_bc', account_path, domain, recipient_address)
    return domain