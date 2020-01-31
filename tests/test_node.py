from aeternity.signing import Account
from aeternity import defaults, identifiers, hashing, utils
import pytest
import random
# from aeternity.exceptions import TransactionNotFoundException


blind_auth_contract = """contract BlindAuth =
      record state = { owner : address }

      entrypoint init(owner' : address) = { owner = owner' }

      stateful entrypoint authorize(r: int) : bool =
        // r is a random number only used to make tx hashes unique 
        switch(Auth.tx_hash)
          None          => abort("Not in Auth context")
          Some(tx_hash) => true

      entrypoint to_sign(h : hash, n : int) : hash =
        Crypto.blake2b((h, n))
    """



def test_node_spend_native(chain_fixture):
    node_cli = chain_fixture.NODE_CLI
    sender_account = chain_fixture.ALICE
    recipient_id = Account.generate().get_address()
    # with numbers 
    tx = node_cli.spend(sender_account, recipient_id, 100)
    print("DATA", tx)
    assert recipient_id == tx.data.tx.data.recipient_id
    assert sender_account.get_address() == tx.data.tx.data.sender_id
    account_balance = node_cli.get_account_by_pubkey(pubkey=recipient_id).balance
    assert account_balance == 100 
    # spend some string 
    tx = node_cli.spend(sender_account, recipient_id, "0.5ae")

    assert recipient_id == tx.data.tx.data.recipient_id
    assert sender_account.get_address() == tx.data.tx.data.sender_id

    account_balance = node_cli.get_account_by_pubkey(pubkey=recipient_id).balance
    assert account_balance == 500000000000000100

def test_node_spend_burst(chain_fixture):
    sender_account = chain_fixture.ALICE
    # make a new non blocking client
    ae_cli = chain_fixture.NODE_CLI
    ae_cli.config.blocking_mode = False
    # recipient account
    recipient_account = Account.generate().get_address()
    # send 50 consecutive spend
    ths = []
    print(">>"*20, "spend burst start")
    for i in range(50):
        tx = ae_cli.spend(sender_account, recipient_account, "1AE")
        ths.append(tx.hash)
    print("<<"*20, "spend burst end")

    for th in ths:
        ae_cli.wait_for_transaction(th)

    assert(ae_cli.get_balance(recipient_account) == utils.amount_to_aettos("50ae"))


@pytest.mark.parametrize("height,protocol_version", [(0, 1), (1, 1), (2, 2), (3, 2), (4, 3), (5, 3)])
def test_node_get_protocol_version(chain_fixture, height, protocol_version):
    # this test assumes that the configuration of the node bein tested has the follwing configuration:
    #   hard_forks:
    #      "1": 0
    #      "2": 2
    #      "3": 4
    assert(chain_fixture.NODE_CLI.get_consensus_protocol_version(height)) == protocol_version

def test_node_ga_attach(chain_fixture, compiler_fixture):
    ae_cli = chain_fixture.NODE_CLI
    account = chain_fixture.ALICE
    c_cli = compiler_fixture.COMPILER
    # test that the account is not already generalized
    poa_account = ae_cli.get_account_by_pubkey(pubkey=account.get_address())
    assert poa_account.kind == identifiers.ACCOUNT_KIND_BASIC
    # transform the account
    # compile the contract
    ga_contract = c_cli.compile(blind_auth_contract).bytecode
    # now encode the call data
    init_calldata = c_cli.encode_calldata(blind_auth_contract, "init", account.get_address()).calldata
    # this will return an object
    # init_calldata.calldata
    # now we can execute the transaction
    tx = ae_cli.account_basic_to_ga(account, ga_contract, calldata=init_calldata)

    # now check if it is a ga
    ga_account = ae_cli.get_account_by_pubkey(pubkey=account.get_address())
    assert ga_account.kind == identifiers.ACCOUNT_KIND_GENERALIZED

def test_node_ga_meta_spend(chain_fixture, compiler_fixture):

    ae_cli = chain_fixture.NODE_CLI
    account = chain_fixture.ALICE
    c_cli = compiler_fixture.COMPILER
    # make the account poa

    # transform the account
    # compile the contract
    ga_contract = c_cli.compile(blind_auth_contract).bytecode
    # now encode the call data
    init_calldata = c_cli.encode_calldata(blind_auth_contract, "init", account.get_address()).calldata
    # this will return an object
    # init_calldata.calldata
    # now we can execute the transaction
    tx = ae_cli.account_basic_to_ga(account, ga_contract, calldata=init_calldata)

    print("ACCOUNT is now GA", account.get_address())

    # retrieve the account data
    ga_account = ae_cli.get_account(account.get_address())
    # create a dummy account
    recipient_id = Account.generate().get_address()

    # generate the spend transactions
    amount = 54321
    payload = "ga spend tx"
    fee = defaults.FEE
    ttl = defaults.TX_TTL

    spend_tx = ae_cli.tx_builder.tx_spend(account.get_address(), recipient_id, amount, payload, fee, ttl, 0)


    # encode the call data for the transaction
    calldata = c_cli.encode_calldata(blind_auth_contract, ga_account.auth_fun, hashing.randint()).calldata
    # now we can sign the transaction (it will use the auth for do that)
    spend_tx = ae_cli.sign_transaction(ga_account, spend_tx, auth_data=calldata)
    # broadcast
    tx_hash = ae_cli.broadcast_transaction(spend_tx)
    print(f"GA_META_TX {tx_hash}")
    # check that the account received the tokens
    assert ae_cli.get_account_by_pubkey(pubkey=recipient_id).balance == amount
