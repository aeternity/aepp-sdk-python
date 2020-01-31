====================
Offline transactions
====================

Throughout this tutorial, we'll walk you through the creation of a basic
script to generate a list of spend transactions and to sign them.

It'll consist of three parts:

* Build a list of spend transactions (offline)
* Sign each transactions (offline)
* Broadcast the transactions obtained in the above steps 

We'll assume you have :doc:`the SDK installed </intro/install>`.


First import the required libraries 

.. literalinclude:: ../../tests/test_tutorial07-offline.py
   :lines: 10-14

For the next steps we need to have an account available.

.. literalinclude:: ../../tests/test_tutorial07-offline.py
   :lines: 18-19
   :dedent: 4

.. hint::
  To successfully complete the tutorial, you will have to have a positive balance on the account just creataed. 
  How to get some funds is :doc:`explained in the first tutorial </intro/tutorial01-spend>` using the `Faucet`_ app.

.. _Faucet: https://testnet.faucet.aepps.com

Once we have an account available we will use the :doc:`TxBuilder </ref/txbuilder>` to prepare the transactions.

.. literalinclude:: ../../tests/test_tutorial07-offline.py
   :lines: 25-50
   :dedent: 4

Once the transactions are ready they need to be signed and encapsulated in signed transaction:

.. hint::
  the Network ID is required to compute a valid signature for transactions; when using the online 
  node client the Network ID is automatically retrieved from the node.

.. literalinclude:: ../../tests/test_tutorial07-offline.py
   :lines: 52-53
   :dedent: 4

The :doc:`TxSigner </ref/txsigner>` object provides the functionality to compute the signature for 
transactions.

.. literalinclude:: ../../tests/test_tutorial07-offline.py
   :lines: 59-69
   :dedent: 4

Finally we can instantiate a node client and broadcast the transactions:


.. literalinclude:: ../../tests/test_tutorial07-offline.py
   :lines: 70-85
   :dedent: 4

.. warn::
   Make sure that you connect to a node that uses the same Network ID that you used before. 
  

.. warn::
  if you intend to broadcast more then 5 transactions for the same account you need to be sure that 
  the node that you are connecting to is configured to accept those transactions  (parameter ``nonce_offset`` in the node configuration)


Thats it! You have successfully executed your transaction in the Aeternity Blockchain testnet network. For the mainnet network the procedure is the same except you will have to get some tokens via an exchange or via other means.


