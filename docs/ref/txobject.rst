============
TxObject
============

``TxObject`` is one of the central entity of the Python SDK,
and it represent a transaction object. 

.. autoclass:: aeternity.transactions.TxObject
   :members: get, meta, ga_meta

The fields of a ``TxObject`` are

- ``hash``: the transaction hash
- ``data``: the transaction data, it varies for every transaction type
- ``metadata``: it contains additional data that may be relevant in the transaction context
- ``tx``: the rlp + base64 check encoded string of the transaction that is used to broadcast a transaction

Since a transaction can be a nested structured, the ``TxObject`` is nested as well:
considering a simple spend transaction, the actual structure of the transaction is:

::

  SignedTx(
    tag:                  - signed transaction type (11)
    version               - transaction version, 1 in this case
    [signature]           - the list of signatures for the signed transaction
    tx: SpendTx(          - the inner spend transaction 
      tag                 - spend transaction type (12) 
      version             - spend transaction version, 1 in this case
      sender_id           - spend sender
      recipient_id        - spend recipient
      amount              - amount being transferred
      fee                 - fee for the miner
      ttl                 - the mempool time to live
      nonce               - sender account nonce
      payload             - arbitrary payload
    )
  )

This means that to access, for example, the spend transaction ``recipient_id`` from a ``TxObject``,
the code would be:

::

  tx_object = node_cli.spend(sender, recipient, "100AE")
  # access the recipient_id
  tx_object.data.tx.data.recipient_id

unless the transaction has been posted from a generalized account, in which case there 
are 4 levels of nesting:

::

  tx_object = node_cli.spend(sender, recipient, "100AE")
  # access the recipient_id for a GA generated transaction
  tx_object.data.tx.data.tx.data.tx.data.recipient_id

This is of course somewhat awkward, and therefore the ``TxObject`` provides the ``get(NAME)``, ``meta(NAME)``, ``ga_meta(NAME)`` functions.

The functions are used to access the values of the properties without worrying about the structure of the transaction,
so the example above will become:

::

  tx_object = node_cli.spend(sender, recipient, "100AE")
  # access the recipient_id for any spend transaction
  tx_object.get("recipient_id")

TODO: document Meta fields

for a complete list of fields here is the list of transactions and available fields:


.. literalinclude:: ../../aeternity/transactions.py
   :lines: 65-389
   :dedent: 4
