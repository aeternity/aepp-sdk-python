from aeternity.signing import Account
from aeternity import defaults
import pytest
# from aeternity.exceptions import TransactionNotFoundException


def _test_node_spend(node_cli, sender_account):
    account = Account.generate().get_address()
    tx = node_cli.spend(sender_account, account, 100)
    assert account == tx.data.recipient_id
    assert sender_account.get_address() == tx.data.sender_id
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


def _poa_to_ga(account, ae_cli, c_cli):
    src = """contract BlindAuth =
      record state = { nonce : int, owner : address }

      function init(owner' : address) = { nonce = 1, owner = owner' }

      stateful function authorize(s : signature) : bool =
        switch(Auth.tx_hash)
          None          => abort("Not in Auth context")
          Some(tx_hash) => 
              put(state{ nonce = state.nonce + 1 })
              true

      function to_sign(h : hash, n : int) : hash =
        Crypto.blake2b((h, n))

      private function require(b : bool, err : string) =
        if(!b) abort(err)
    """
    # compile the contract
    ga_contract = c_cli.compile(src).bytecode
    # this will return an object

    # now encode the call data
    init_calldata = c_cli.encode_calldata(src, "init", [account.get_address()]).calldata
    # this will return an object
    # init_calldata.calldata

    # now we can execute the transaction
    tx = ae_cli.poa_to_ga(account, ga_contract, init_calldata=init_calldata, gas=500)
    return tx


def test_node_ga_attach(chain_fixture, compiler_fixture):

    ae_cli = chain_fixture.NODE_CLI
    account = chain_fixture.ACCOUNT
    c_cli = compiler_fixture.COMPILER
    # test that the account is not already generalized
    poa_account = ae_cli.get_account_by_pubkey(pubkey=account.get_address())
    assert poa_account.kind == "basic"
    # transform the account
    tx = _poa_to_ga(account, ae_cli, c_cli)
    # now check if it is a ga
    ga_account = ae_cli.get_account_by_pubkey(pubkey=account.get_address())
    assert ga_account.kind == "generalized"


def test_node_ga_meta_spend(chain_fixture, compiler_fixture):

    ae_cli = chain_fixture.NODE_CLI
    account = chain_fixture.ACCOUNT
    c_cli = compiler_fixture.COMPILER
    # make the account poa
    tx = _poa_to_ga(account, ae_cli, c_cli)
    # retrieve the account data
    ga_account = ae_cli.get_account_by_pubkey(pubkey=account.get_address())
    contract_id = ga_account.contract_id
    auth_fun = ga_account.auth_fun
    # create a dummy account
    recipient_id = Account.generate().get_address()
    # generate the spend transactions
    amount = 54321
    payload = "ga spend tx"
    fee = defaults.FEE
    ttl = defaults.TX_TTL
    nonce = 0
    spend_tx = ae_cli.tx_builder.tx_spend(account.get_address(), recipient_id, amount, payload, fee, ttl, 0)
    spend_tx = sign_transaction(account, spend_tx.tx)
    print(spend_tx)
    # encode the call data for the transaction
    calldata = c_cli.encode_calldata(src, "authorize", [account.get_address()]).calldata
    # now we can execute the transaction
    tx = ae_cli.ga_meta(account, ga_contract, init_calldata=init_calldata, gas=500)
    ga_account = ae_cli.get_account_by_pubkey(pubkey=account.get_address())
    assert ga_account.kind == "generalized"
    raise ValueError()
