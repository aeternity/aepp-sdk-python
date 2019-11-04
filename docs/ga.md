# Generalized Accounts

This page describe how to use the Python SDK to convert a basic account to a generalized one.
For additional information about genrealized accounts visit the [documentation](https://github.com/aeternity/protocol/blob/master/generalized_accounts/ga_explained.md).



## Example

The following example describe how to transform a basic account to a generalized one and
how to execute a spend transaction from a generalized account.


```python
from aeternity.node import NodeClient, Config
from aeternity.signing import Account
from aeternity.transactions import TxBuilder
from aeternity.compiler import CompilerClient
from aeternity import defaults, hashing, utils

import requests



def top_up_account(account_address):

    print()
    print(f"top up account {account_address} using the testnet.faucet.aepps.com app")
    r = requests.post(f"https://testnet.faucet.aepps.com/account/{account_address}").json()
    tx_hash = r.get("tx_hash")
    balance = utils.format_amount(r.get("balance"))
    print(f"account {account_address} has now a balance of {balance}")
    print(f"faucet transaction hash {tx_hash}")
    print()



def main():

    """
    This example is divided in 2 parts
    - the first one is about transforming a Basic account to Generalized
    - the second shows how to post transactions from GA accounts
    """

    #
    # PART 1: fro Basic to GA
    #
    print("Part #1 - transform a Basic account to a Generalized one")
    print()

    # first we create a new account
    # this will be the ga account
    print(f"generate a new account")
    ga_account = Account.generate()
    print(f"your basic account address is {ga_account.get_address()}")

    # use the faucet to top up your ga account
    top_up_account(ga_account.get_address())

    # Instantiate a node client
    node_url = "http://sdk-testnet.aepps.com"
    print(f"using node at {node_url}")
    # get the node client
    n = NodeClient(Config(
        external_url=node_url,
        blocking_mode=True # we want the client to verify the transactions are included in the chain
    ))


    # we are going to use a contract that will not be performing
    # any real authorization, just to provide a proof of concept
    # for the ga interaction
    #
    # DO NOT USE THIS CONTRACT IN A REAL SCENARIO
    # DO NOT USE THIS CONTRACT IN A REAL SCENARIO
    # DO NOT USE THIS CONTRACT IN A REAL SCENARIO
    #
    # this contract authorizes anybody to perform transactions
    # using the funds of the account!
    #
    blind_auth_contract = """contract BlindAuth =
    record state = { owner : address }

    entrypoint init(owner' : address) = { owner = owner' }

    stateful entrypoint authorize(r: int) : bool =
        // r is a random number only used to make tx hashes unique
        switch(Auth.tx_hash)
            None          => abort("Not in Auth context")
            Some(tx_hash) => true
    """

    # Instantiate a compiler client
    compiler_url = "https://compiler.aepps.com"
    print(f"using compiler at {compiler_url}")
    # get the node client
    c = CompilerClient(compiler_url=compiler_url)

    print()

    # compile the contract for the ga an retrieve the bytecode
    print("compile ga contract")
    bytecode = c.compile(blind_auth_contract).bytecode

    # prepare the calldata for the init function
    print("encode the init function calldata")
    init_calldata = c.encode_calldata(blind_auth_contract, "init", [ga_account.get_address()]).calldata

    # now we execute the first step, we'll be transforming the account into a ga
    print("execute the GaAttach transaction")
    ga_attach_tx = n.account_basic_to_ga(
        ga_account, # the ga account
        bytecode, # the bytecode of the ga contract
        init_calldata=init_calldata, # the encoded parameters of the init function
        auth_fun="authorize", # the name of the authentication function to use from the contract
        gas=1000
    )
    print(f"GaAttachTx hash is {ga_attach_tx.hash}")
    print(f"the account {ga_account.get_address()} is now generalized")

    #
    # END of PART 1
    #

    print()

    #
    # PART 2: posting a transaction from a GA account
    #
    # In this part we will be creating a spend transaction and we'll transfer 4AE
    # from the generalized account to a newly created account
    #
    print("Part #2 - Create a spend transaction from a GA account")
    print()

    # we will be using the compiler client and the node client from the PART 1

    # first we create a new account
    # this will be the recipient account
    rc_account_address = "ak_2iBPH7HUz3cSDVEUWiHg76MZJ6tZooVNBmmxcgVK6VV8KAE688"
    print(f"the recipient account address is {rc_account_address}")

    # then we prepare the parameters for a spend transaction
    sender_id = ga_account.get_address() # the ga sendder account
    amount = 4000000000000000000 # we will be sending 4.9AE
    payload = "" # we'll be sending an empty payload
    fee = defaults.FEE # we'll use the default fee (the client will generate the right fee for us)
    ttl = defaults.TX_TTL # we'll use the default ttl for the transaction
    nonce = defaults.GA_ACCOUNTS_NONCE # we'll use 0 as nonce since is is a special case

    # now we'll use the builder to prepare the spend transaction
    print(f"prepare a spend transaction from {sender_id} to {rc_account_address} of {utils.format_amount(amount)}")
    builder = TxBuilder()
    spend_tx = builder.tx_spend(sender_id, rc_account_address, amount, payload, fee, ttl, nonce)

    # now that we have the transaction we need to prepare the authentication data for the ga transaction
    print("encode the authorize function calldata")
    auth_calldata = c.encode_calldata(blind_auth_contract, "authorize", [hashing.randint()]).calldata

    # and use the sign_transaction with the auth_calldata to automatically
    # prepare the ga transaction for us
    print("execute the GaMeta transaction")
    ga_meta_tx = n.sign_transaction(ga_account, spend_tx, auth_data=auth_calldata)

    # and finally we can broadcast the transaction
    ga_meta_tx_hash = n.broadcast_transaction(ga_meta_tx)
    print(f"GaMetaTx hash is {ga_meta_tx_hash}")
    print(f"the account spend transaction has been executed")

    # note that you can verify all the steps above using the command line client
    print()
    print("Verify the steps using the command line client")
    print("1. Check the ga account:")
    print(f"aecli inspect {ga_account.get_address()}")
    print("2. Check the GaAttachTx:")
    print(f"aecli inspect {ga_attach_tx.hash}")
    print("3. Check the GaMetaTx:")
    print(f"aecli inspect {ga_meta_tx_hash}")


if __name__ == "__main__":
    main()
```
