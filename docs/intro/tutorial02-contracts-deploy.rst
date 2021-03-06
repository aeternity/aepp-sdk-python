====================
Deploying a contract
====================

This guide describes how you can leverage aepp-sdk to compile and
deploy an aeternity smart contracts.

.. seealso:: Sophia: An Æternity Blockchain Language

                The Sophia is a language in the ML family.
                It is strongly typed and has restricted mutable state.
                Check out more about sophia `here <https://github.com/aeternity/protocol/blob/master/contracts/sophia.md>`_.


Prerequisites
=============

1. An account with some initial AE
2. A smart contract written in sophia
3. An aeternity node
4. A sophia aehttp compiler

.. admonition:: Assumptions

                We're going to assume that you have working knowledge of the SDK and
                know how to create an Account instance, a NodeClient, and a CompilerClient.


Sample Sophia Contract
======================

Below is the sample sophia contract that we'll use in this guide.

.. literalinclude:: ../../tests/testdata/CryptoHamster.aes

Importing required classes and methods
======================================

We need to import the following classes to use contracts. 

.. literalinclude:: ../../tests/test_tutorial05-contracts.py
   :lines: 11-14


Initializing NodeClient and Compiler
====================================

Below are the steps required to initialize the `NodeClient` and `Compiler`.
As you can see below, during the initialization of `NodeClient` we're also providing the `internal_url`. 

`internal_url` provides the debug endpoint to `dry_run` a contract method which 
can also be used to do static calls on deployed contracts and this is what exactly we're going to use this for.

You can also not provide the `internal_url` but then you'll have to disable the use of `dry-run` endpoint.
We'll see how to do that when we initialize our contract.

.. literalinclude:: ../../tests/test_tutorial05-contracts.py
   :lines: 18-28
   :dedent: 4

Generate an Account
=====================

You'll need an account (using the `Account` class) to deploy the contract and also for stateful contract calls.

.. literalinclude:: ../../tests/test_tutorial05-contracts.py
   :lines: 32-33
   :dedent: 4

Read the Contract from file and initialize
==========================================

You can read the contract from the stored `.aes` file and use it to initialize the contract instance.
If you have not provided the `internal_endpoint` or simple do not want to use the `dry-run` functionality
you can disable it by passing `use-dry-run=False` to the `ContractNative` constructor.

.. warning::
                If you DO NOT provide the `internal_url` during NodeClient initialization
                and also DID NOT disable the `dry-run` then the contract method calls for
                `un-stateful` methods WILL FAIL.

.. literalinclude:: ../../tests/test_tutorial05-contracts.py
   :lines: 37-52
   :dedent: 4

Compile and deploy the contract
===============================

You can compile the contract and deploy it using the `deploy` method.
If your `init` method accepts any arguments then please provide them inside the `deploy` method.
Once the contract is compiled and deployed, the signed transaction is returned.

.. literalinclude:: ../../tests/test_tutorial05-contracts.py
   :lines: 53-57
   :dedent: 4


Thats all, you have successfully deployed a smart contract in Aeternity, the next tutorial
will guide you to call the contract

