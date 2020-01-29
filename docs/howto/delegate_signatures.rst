=================================
Transaction delegation signatures
=================================

The `Sophia`_ language for smart contracts allow to delegate
the transaction execution to a contract by providing 
delegation signatures.

.. _Sophia: https://github.com/aeternity/protocol/blob/aeternity-node-v5.4.1/contracts/sophia.md

Delegate signatures for AENS
============================

The following code snippet shows how to generate 
signatures for name transactions delegation to a contract

::

  # import the required libraries
  from aeternity.node import NodeClient, Config
  from aeternity.signing import Account

  # initialize the node client
  node_cli = NodeClient(Config(external_url="https://mainnet.aeternal.io"))
  
  # get an account 
  account = Account.from_keystore("/path/to/keystore", "keystore password")

  # an example name
  name = "example.chain"
 
  # name preclaim signature delegation
  sig = node_cli.delegate_name_preclaim_signature(account, contract_id)
  
  # name claim signature delegation
  sig = node_cli.delegate_name_claim_signature(account, contract_id, name)
  
  # name revoke signature delegation
  sig = node_cli.delegate_name_revoke_signature(account, contract_id, name)
  
  # name revoke signature delegation
  sig = node_cli.delegate_name_transfer_signature(account, contract_id, name)
  

Delegate signatures for Oracles
===============================

The following code snippet shows how to generate 
signatures for oracle transactions delegation to a contract

::

  # import the required libraries
  from aeternity.node import NodeClient, Config
  from aeternity.signing import Account

  # initialize the node client
  node_cli = NodeClient(Config(external_url="https://mainnet.aeternal.io"))
  
  # get an account 
  account = Account.from_keystore("/path/to/keystore", "keystore password")
 
  # name preclaim signature delegation
  sig = node_cli.delegate_oracle_register_signature(account, contract_id)
  
  # name claim signature delegation
  sig = node_cli.delegate_oracle_extend_signature(account, contract_id)
  
  # example query id
  query_id = "oq_......"

  # name revoke signature delegation
  sig = node_cli.delegate_oracle_respond_signature(account, contract_id, query_id)
  


