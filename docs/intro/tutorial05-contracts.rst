======================
Working with Contracts
======================

This guide describes how you can leverage aepp-sdk to compile,
deploy and interact with aeternity smart contracts.

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

We need to import the following classes to use contracts. 

.. literalinclude:: ../../tests/test_tutorial05-contracts.py
   :lines: 11-14
   :dedent: 4

Initializing NodeClient and Compiler
====================================

Below are the steps required to initialize the the `NodeClient` and `Compiler`.
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

You can read the contract from the stored `.aes` file and use it to initilaize the contract instance.
If you have not provided the `internal_endpoint` or simple do not want to use the `dry-run` functionality
you can disable it by passing `use-dry-run=False` to the `ContractNative` constructor.

.. warning::
                If you DO NOT provide the `internal_url` during NodeClient initialization
                and also DID NOT disable the `dry-run` then the contract method calls for
                `un-stateful` methods WILL FAIL.

.. literalinclude:: ../../tests/test_tutorial05-contracts.py
   :lines: 37-48
   :dedent: 4

Compile and deploy the contract
===============================

You can compile the contract and deploy it using the `deploy` method.
If your `init` method accepts any arguments then please provide them inside the `deploy` method.
Once the contract is compiled and deployed, the signed transaction is returned.

.. literalinclude:: ../../tests/test_tutorial05-contracts.py
   :lines: 50-51
   :dedent: 4

Call the contract methods
=========================

Once the contract is deployed, all the methods inside the contract are
also available (with same signature) to use from the contract instance.

.. note:: 
                All the methods that are NOT `stateful`, by default are processed using the `dry-run` endpoint to save gas.
                And therefore, a transaction hash will also not be provided for them.
                This functionality can be either diabled for the contract instance or per method by using `use_dry_run` argument.

.. literalinclude:: ../../tests/test_tutorial05-contracts.py
   :lines: 53-57
   :dedent: 4
.. literalinclude:: ../../tests/test_tutorial05-contracts.py
   :lines: 62-65
   :dedent: 4
=======

.. code-block:: OCAML

    contract CryptoHamster =

        record state = {
            index : int, 
            map_hamsters : map(string, hamster), 
            testvalue: int}

        record hamster = {
            id : int,
            name : string,
            dna : int}

        stateful entrypoint init() = 
            { index = 1,
                map_hamsters = {},
                testvalue = 42}

        public entrypoint read_test_value() : int =
            state.testvalue

        public entrypoint return_caller() : address =
            Call.caller

        public entrypoint cause_error() : unit =
            require(2 == 1, "require failed") 

        public stateful entrypoint add_test_value(one: int, two: int) : int =
            put(state{testvalue = one + two})
            one + two

        public entrypoint locally_add_two(one: int, two: int) : int =
            one + two

        public stateful entrypoint statefully_add_two(one: int, two: int) =
            put(state{testvalue = one + two})

        stateful entrypoint create_hamster(hamster_name: string) =
            require(!name_exists(hamster_name), "Name is already taken")
            let dna : int = generate_random_dna(hamster_name)
            create_hamster_by_name_dna(hamster_name, dna)

        entrypoint name_exists(name: string) : bool =
            Map.member(name, state.map_hamsters)

        entrypoint get_hamster_dna(name: string, test: option(int)) : int =
            require(name_exists(name), "There is no hamster with that name!")

            let needed_hamster : hamster = state.map_hamsters[name]

            needed_hamster.dna

        private stateful function create_hamster_by_name_dna(name: string, dna: int) =
            let new_hamster : hamster = {
                id = state.index,
                name = name,
                dna = dna}

            put(state{map_hamsters[name] = new_hamster})
            put(state{index = (state.index + 1)})

        private function generate_random_dna(name: string) : int =
            get_block_hash_bytes_as_int() - Chain.timestamp + state.index

        private function get_block_hash_bytes_as_int() : int =
            switch(Chain.block_hash(Chain.block_height - 1))
                None => abort("blockhash not found")
                Some(bytes) => Bytes.to_int(bytes)

        entrypoint test(name: string) : hash =
            String.sha3(name)
