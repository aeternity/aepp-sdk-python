=======================
Accounts and Signatures
=======================

The Aeternity blockchain uses the account/balance model,
and here are listed all the possibility regarding handling
accounts and signatures


Create an account (non HD) 
==========================

Generate a new account

::

  # import the Account class from signing
  from aeternity.signing import Account

  account = Account.generate()
  print(account) # will print the public key/address of the account

Save account on file
====================

::

  # import the Account class from signing
  from aeternity.signing import Account

  # generate a new account
  account = Account.generate()

  # save to file
  account.save_to_keystore_file("keystore_file_path", "My Password")

Load account
=======================

::

  # import the Account class from signing
  from aeternity.signing import Account

  # load from file
  account = Account.from_keystore("keystore_file_path", "My Password")

  # from secret key string hex encoded
  account = Account.from_secret_key_string("mysecretkeystring...")


To synchronize an Account with data from
the node, such as the account type (Basic or GA)

::

  # import the Account class from signing
  from aeternity.node import NodeClient, Config

  # initialize the node client
  node_cli = NodeClient()

  # synchronize with the node api
  account = node_cli.get_account(keystore_path="", password="", height="")
  




Print the secret key of an account
==================================

.. warning::
  The secret key is printed in "plain text", by printing it on the terminal or saving
  it without encryption you expose your account


the command to print the public and secret key of an account saved in a keystore file is:

::
  
  $ aecli account address --secret-key KEYSTORE_FILENAME.json

Example:

::

  ➜ aecli account address BOB.json --secret-key
  Enter the account password: 
  !Warning! this will print your secret key on the screen, are you sure? [y/N]: y
  <account>
    Address ___________________________________________ ak_2P44NhGFT7fP1TFpZ62FwabWP9djg5sDwFNDVVpiGgd3p4yA7X
    Secretkey _________________________________________ c226bf650f30740287f77a715............f49ddff758971112fb5cfb0e66975a8f
  </account>


