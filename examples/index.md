# Examples

## Spend transaction (programmatically)

The sample will use `testnet`

### Before you start

Will be using a newly created account for the following example. The first account will be the sender account.

```python

from aeternity import signing
# generate a new account
sender_account = signing.Account.generate()
# save the account in an encrypted format
sender_account.save_to_keystore_file("sender_account.json", "mypassword")
# print the account address
print("Sender account address: ", sender_account.get_address())

```

Go to [testnet.faucet.aepps.com](testnet.faucet.aepps.com) and paste there the sender account address 

### First example: easy spend transaction

The account created at this step will be the recipient account

```python

from aeternity import signing, node

# open the sender account
sender_account = signing.Account.from_keystore("sender_account.json", "mypassword")
# generate a new account
recipient_account = signing.Account.generate()

# initialize a node client
aeternity_cli = node.NodeClient(node.Config(
    external_url="https://sdk-testnet.aepps.com",
    network_id="ae_uat"  # optional
))
# now build the transaction
tx = aeternity_cli.spend(sender_account,
                         recipient_account.get_address(),
                         1000000000000000000
                         )
print(f"https://testnet.explorer.aepps.com/#/tx/{tx.hash}")


```

## Secound example: 3 steps spend transaction

```python

from aeternity import transactions, signing, node, identifiers

# open the sender account
sender_account = signing.Account.from_keystore("sender_account.json", "mypassword")
# generate a new account
recipient_account = signing.Account.generate()


# Step 1: build the transaction

# in this case we have to know the nonce before
# since building the transaction is performed offline
nonce = 2

tx_builder = transactions.TxBuilder()
tx = tx_builder.tx_spend(sender_account.get_address(),
                         recipient_account.get_address(),
                         1000000000000000000,
                         "test tx",
                         0,  # fee, when 0 it is automatically computed
                         0,  # ttl for the transaction in number of blocks (default 0)
                         nonce)

# Step 2: sign the transaction
tx_signer = transactions.TxSigner(
    sender_account,
    identifiers.NETWORK_ID_TESTNET  # ae_uat
)
tx_signed = tx_signer.sign_encode_transaction(tx)


# Step 3: broadcast the transaction

# initialize a node client
aeternity_cli = node.NodeClient(node.Config(
    external_url="https://sdk-testnet.aepps.com",
))

# broadcast the transaction
aeternity_cli.broadcast_transaction(tx_signed.tx, tx_signed.hash)

print(f"https://testnet.explorer.aepps.com/#/tx/{tx_signed.hash}")
print(f"now waiting for confirmation (it will take ~9 minutes)...")

# Step 4: [optional] wait for transaction verification
# the default will wait 3 blocks after the transaction generation blocks
# the confirmation blocks number can be changed passing the 
# key_block_confirmation_num
# parameter to teh node.Config
aeternity_cli.wait_for_confirmation(tx_signed.hash)

print(f"transaction confirmed!")

```
