from aeternity.signing import Account
from aeternity import defaults, identifiers, hashing
import pytest
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


def _test_node_spend(node_cli, sender_account):
    account = Account.generate().get_address()
    tx = node_cli.spend(sender_account, account, 100)
    print("DATA", tx)
    assert account == tx.data.tx.data.recipient_id
    assert sender_account.get_address() == tx.data.tx.data.sender_id
    account = node_cli.get_account_by_pubkey(pubkey=account)
    balance = account.balance
    assert balance > 0


def test_node_spend_native(chain_fixture):
    _test_node_spend(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)


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
    account = chain_fixture.ACCOUNT
    c_cli = compiler_fixture.COMPILER
    # test that the account is not already generalized
    poa_account = ae_cli.get_account_by_pubkey(pubkey=account.get_address())
    assert poa_account.kind == identifiers.ACCOUNT_KIND_BASIC
    
    # transform the account
    # compile the contract
    ga_contract = c_cli.compile(blind_auth_contract).bytecode
    # now encode the call data
    init_calldata = c_cli.encode_calldata(blind_auth_contract, "init", [account.get_address()]).calldata
    # this will return an object
    # init_calldata.calldata
    # now we can execute the transaction
    tx = ae_cli.account_basic_to_ga(account, ga_contract, init_calldata=init_calldata, gas=500)

    # now check if it is a ga
    ga_account = ae_cli.get_account_by_pubkey(pubkey=account.get_address())
    assert ga_account.kind == identifiers.ACCOUNT_KIND_GENERALIZED


def test_node_ga_meta_spend(chain_fixture, compiler_fixture):

    ae_cli = chain_fixture.NODE_CLI
    account = chain_fixture.ACCOUNT
    c_cli = compiler_fixture.COMPILER
    # make the account poa
    
    # transform the account
    # compile the contract
    ga_contract = c_cli.compile(blind_auth_contract).bytecode
    # now encode the call data
    init_calldata = c_cli.encode_calldata(blind_auth_contract, "init", [account.get_address()]).calldata
    # this will return an object
    # init_calldata.calldata
    # now we can execute the transaction
    tx = ae_cli.account_basic_to_ga(account, ga_contract, init_calldata=init_calldata, gas=500)

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
    calldata = c_cli.encode_calldata(blind_auth_contract, ga_account.auth_fun, [hashing.randint()]).calldata
    # now we can sign the transaction (it will use the auth for do that)
    spend_tx = ae_cli.sign_transaction(ga_account, spend_tx, auth_data=calldata)
    # broadcast
    tx_hash = ae_cli.broadcast_transaction(spend_tx)
    print(f"GA_META_TX {tx_hash}")
    # check that the account received the tokens
    assert ae_cli.get_account_by_pubkey(pubkey=recipient_id).balance == amount
