==========================
Transfer funds
==========================


Let's learn by example.

Throughout this tutorial, we'll walk you through the creation of a basic
script to transfer funds from an account to another. 

It'll consist of three parts:

* Generate 2 accounts via command line client
* Get some funds for the first account
* Transfer the funds from an account to the other

We'll assume you have :doc:`the SDK installed </intro/install>` already. You can
tell the SDK is installed and which version by running the following command
in a shell prompt (indicated by the $ prefix):

::

    $ aecli --version

First step will be to generate two new accounts using the command line client:

First import the required libraries 

.. literalinclude:: ../../tests/test_tutorial01-spend.py
   :lines: 9-14

Then instantiate the node client and generate 2 accounts

.. literalinclude:: ../../tests/test_tutorial01-spend.py
   :lines: 16-39
   :dedent: 4


Now copy the Alice address and paste it into the `Aeternity Faucet`_ to top up the account; once the Alice account has some positive balance we can execute the spend transaction:


.. _Aeternity Faucet: https://testnet.faucet.aepps.com


.. literalinclude:: ../../tests/test_tutorial01-spend.py
   :lines: 45-51
   :dedent: 4

And finally verify the new balance:

.. literalinclude:: ../../tests/test_tutorial01-spend.py
   :lines: 56-63
   :dedent: 4

Thats it! You have successfully executed your transaction in the Aeternity Blockchain testnet network. For the mainnet network the procedure is the same except you will have to get some tokens via an exchange or via other means.
