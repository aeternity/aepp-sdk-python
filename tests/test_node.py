from aeternity.signing import Account
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


def test_node_ga_attach(chain_fixture, compiler_fixture):
    src = """contract BlindAuth =
      record state = { nonce : int, owner : address }

      function init(owner' : address) = { nonce = 1, owner = owner' }

      stateful function authorize(n : int, s : signature) : bool =
        switch(Auth.tx_hash)
          None          => abort("Not in Auth context")
          Some(tx_hash) => 
              put(state{ nonce = n + 1 })
              true

      function to_sign(h : hash, n : int) : hash =
        Crypto.blake2b((h, n))

      private function require(b : bool, err : string) =
        if(!b) abort(err)
    """
    ae_cli = chain_fixture.NODE_CLI
    account = chain_fixture.ACCOUNT
    c_cli = compiler_fixture.COMPILER
    # test that the account is not already generalized
    poa_account = ae_cli.get_account_by_pubkey(pubkey=account.get_address())
    assert poa_account.kind == "basic"

    # compile the contract
    ga_contract = c_cli.compile(src).bytecode
    # this will return an object 
    # ga_contract.bytecode

    # now encode the call data
    init_calldata = c_cli.encode_calldata(src, "init", [account.get_address()]).calldata
    # this will return an object
    # init_calldata.calldata

    # now we can execute the transaction
    tx = ae_cli.poa_to_ga(account, ga_contract, init_calldata=init_calldata, gas=500)
    print(tx)
    # print(tx)
    ga_account = ae_cli.get_account_by_pubkey(pubkey=account.get_address())
    assert ga_account.kind == "generalized"
