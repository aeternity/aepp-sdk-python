=======================
Code Snippets
=======================


This is a collection of code snippets and scripts that may 
be used for copy/paste or quick references.


Top up account from the Faucet
==============================

Code to programmatically top-up an account using the `Faucet`_

.. _faucet: https://testnet.faucet.aepps.com

.. code-block:: python
   
  def top_up_account(account_address):

    print(f"top up account {account_address} using the testnet.faucet.aepps.com app")
    r = requests.post(f"https://testnet.faucet.aepps.com/account/{account_address}").json()
    tx_hash = r.get("tx_hash")
    balance = utils.format_amount(r.get("balance"))
    print(f"account {account_address} has now a balance of {balance}")
    print(f"faucet transaction hash {tx_hash}")


Generate multiple accounts
===============================

The following is a command line tool to generate multiple accounts
and to export the accounts secret/public keys.
Useful for testing


.. literalinclude:: accounts.py
   
