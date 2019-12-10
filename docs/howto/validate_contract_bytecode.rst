==========================
Validate contract bytecode
==========================

When deploying a contract on the aeternity blockchain
you have to compile the source into bytecode and
then create a transaction that includes this bytecode.
But when the contract is deployed, aeternity node initializes
the contract using the provided `init` method and then removes
it from the bytecode before storing it on the chain.
Therefore, given the contract source and it's address on
the network you cannot verify the source.

To overcome this behaviour and validate the bytecode,
you can refer to the below example:

.. note::
                This method is only available if you are using compiler version >= 4.1.0.


Deploy the contract (if it is not already)
==========================================

.. literalinclude:: ../../tests/test_compiler.py
   :lines: 125-132
   :dedent: 4

Validate the contract
=====================

.. literalinclude:: ../../tests/test_compiler.py
   :lines: 134-136
   :dedent: 4