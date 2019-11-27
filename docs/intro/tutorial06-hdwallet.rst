================================
Generating and using a HD Wallet
================================

This tutorial covers the generation, use and management
of a HD Wallet using aepp-sdk.

.. note::
        Do not know what HD Wallets are?
        You can read about it `here <https://en.bitcoin.it/wiki/Deterministic_wallet>`_.

Importing the HD Wallet class
=============================

.. literalinclude:: ../../tests/test_tutorial06-hdwallet.py
   :lines: 1-1

Generating a Mnemonic
======================

The HdWallet class exposes a static method to generate
a BIP39 compatible mnemonic seed phrase.

.. literalinclude:: ../../tests/test_tutorial06-hdwallet.py
   :lines: 5-6
   :dedent: 4

Generating a HD Wallet
======================

You can instantiate a HDWallet instance by using the
`HDWallet` class.
The constructor accepts a mnemonic seed phrase and
if no seed phrase is provided then one is auto generated.

.. literalinclude:: ../../tests/test_tutorial06-hdwallet.py
   :lines: 10-12
   :dedent: 4

Deriving a child private key
============================

Once the HD wallet is instantiated, you can access the
provided class method to derive child private/secret keys.

.. literalinclude:: ../../tests/test_tutorial06-hdwallet.py
   :lines: 16-20
   :dedent: 4
