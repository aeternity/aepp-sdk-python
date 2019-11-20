============================
Command Line Interface (CLI)
============================

We'll assume you have :doc:`the SDK installed </intro/install>` already. You can
tell the SDK is installed and which version by running the following command
in a shell prompt (indicated by the $ prefix):

CLI Usage
=========

See below for programmatic usage

You can launch the command line tool using

::

  $ aecli


Available commands:

::

  Usage: aecli [OPTIONS] COMMAND [ARGS]...

    Welcome to the aecli client.

    The client is to interact with an node node.

  Options:
    --version            Show the version and exit.
    -u, --url URL        Node node url
    -d, --debug-url URL
    --force              Ignore node version compatibility check
    --wait               Wait for transactions to be included
    --json               Print output in JSON format
    --version            Show the version and exit.
    --help               Show this message and exit.

  Commands:
    account  Handle account operations
    chain    Interact with the blockchain
    config   Print the client configuration
    inspect  Get information on transactions, blocks,...
    name     Handle name lifecycle
    oracle   Interact with oracles
  tx       Handle transactions creation


## Environment variables

Use the environment variables

- ``NODE_URL``
- ``NODE_URL_DEBUG``

Example usage
=============

The following is a walkthrough
to execute a spend transaction on the testnet_ network

.. _testnet: https://testnet.aeternal.io

#. Set the environment variables

::

  $ export NODE_URL=https://testnet.aeternity.io


❗ When not set the command line client will connect to mainnet

#. Retrieve the top block

::

  $ aecli chain top
  <top for node at https://testnet.aeternity.io >
    Hash ______________________________________________ mh_2GKNC4Nft3mTtiUizsgmNySM6bmrtEk47AFd7QYxGLni6dHuSH
    Height ____________________________________________ 171074
    Pof hash __________________________________________ no_fraud
    Prev hash _________________________________________ mh_2C1qtupSRTGhfgXStkFgPgTU7EtRpbj3R6JeqY94mKDnUM5erw
    Prev key hash _____________________________________ kh_2mMnrh68xvs25qqnY6Q6BCYPPGEfW2AshvThNDugut12KGCjTp
    Signature _________________________________________ sg_UGs78hj7QJ96TZR4vLmrUPmXW2STFPQCR49q1mEvyEHWotC1k8DB6qfqwJGFjRtZL27rSEitLRee5wCqbs4XtGVZAFiCk
    State hash ________________________________________ bs_2ZvCLwHsVPkEn43qvviRpr1vQ1snpGd1izex6kScbU2Zd99s9S
    Time ______________________________________________ 2019-11-20T11:11:22.934000+00:00
    Txs hash __________________________________________ bx_D4Y9x2RjobeCEETZqbVgYFsNu6UKhdSTAJXdXZBb5JbAuW7QA
    Version ___________________________________________ 4
  </top for node at https://testnet.aeternity.io >

#. Create a new account

::

  $ aecli account create Bob.json
  Enter the account password []:
  <account>
    Address ___________________________________________ ak_BobY97QUVR4iDLg4k3RKmy6shZYx9FR75nLaN33GsVmSnhWxn
    Path ______________________________________________ /.../Bob.json
  </account>


❗ Make sure that you use a long and difficult-to-guess password for an account that you plan to use on mainnet

#. Go to [testnet.faucet.aepps.com](https://testnet.faucet.aepps.com) and top up your account

#. Inspect the transaction reported by the faucet app

::

  $ aecli inspect th_2CV4a7xxDYj5ysaDjXNoCSLxnkowGM5bbyAvtdoPvHZwTSYykX
  <transaction>
    <data>
      Block height ____________________________________ 12472
      Block hash ______________________________________ mh_2vjFffExUZPVGo3q6CHRSzxVUhzLcUnQQUWpijFtSvKfoHwQWe
      Hash ____________________________________________ th_2CV4a7xxDYj5ysaDjXNoCSLxnkowGM5bbyAvtdoPvHZwTSYykX
      <signatures 1>
        Signature #1 __________________________________ sg_WtPeyKWN4zmcnZZXpAxCT8EvjF3qSjiUidc9cdxQooxe1JCLADTVbKDFm9S5bNwv3yq57PQKTG4XuUP4eTzD5jymPHpNu
      </signatures>
      <tx>
        <data>
          Amount ______________________________________ 5AE
          Fee _________________________________________ 2.0000E-14AE
          Nonce _______________________________________ 146
          Payload _____________________________________ ba_RmF1Y2V0IFR4tYtyuw==
          Recipient id ________________________________ ak_2ioQbdSViNKjknaLUWphdRjpbTNVpMHpXf9X5ZkoVrhrCZGuyW
          Sender id ___________________________________ ak_2iBPH7HUz3cSDVEUWiHg76MZJ6tZooVNBmmxcgVK6VV8KAE688
          Ttl _________________________________________ 12522
          Type ________________________________________ SpendTx
          Version _____________________________________ 1
          Tag _________________________________________ 12
        </data>
        <metadata>
          Min fee _____________________________________ 0.00001706AE
        </metadata>
        Tx ____________________________________________ tx_+GEMAaEB4TK48d23oE5jt/qWR5pUu8UlpTGn8bwM5JISGQMGf7ChAeKbvpV6jbxy/le3tbquBoRjk0ehgOsRdSzc09bKfw3uiEVjkYJE9AAAgk4ggjDqgZKJRmF1Y2V0IFR47rafGA==
      </tx>
      Tag _____________________________________________ 11
      Type ____________________________________________ SignedTx
      Version _________________________________________ 1
    </data>
    Tx ________________________________________________ tx_+KsLAfhCuEDkb9XQq/ihtZ+DNbDBI/9ntVGwcJJLCV0qZE8c9wMxAeTyyG3hVqthIco/NLuaVQ0N3XRYhYb6PsYOjAf8hzMJuGP4YQwBoQHhMrjx3begTmO3+pZHmlS7xSWlMafxvAzkkhIZAwZ/sKEB4pu+lXqNvHL+V7e1uq4GhGOTR6GA6xF1LNzT1sp/De6IRWORgkT0AACCTiCCMOqBkolGYXVjZXQgVHgQZGwg
    Hash ______________________________________________ th_2CV4a7xxDYj5ysaDjXNoCSLxnkowGM5bbyAvtdoPvHZwTSYykX
  </transaction>


#. Create another account

::
  $ aecli account create Alice.json
  Enter the account password []:
  <account>
    Address ___________________________________________ ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
    Path ______________________________________________ /.../Alice.json
  </account>



#. Transfer some tokens to an account to the other

::
  $ aecli account spend Bob.json ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M 1AE
  Enter the account password []:
  <spend transaction>
    <data>
      Tag _____________________________________________ 12
      Vsn _____________________________________________ 1
      Sender id _______________________________________ ak_BobY97QUVR4iDLg4k3RKmy6shZYx9FR75nLaN33GsVmSnhWxn
      Recipient id ____________________________________ ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
      Amount __________________________________________ 1AE
      Fee _____________________________________________ 0.00001686AE
      Ttl _____________________________________________ 0
      Nonce ___________________________________________ 4
      Payload _________________________________________
    </data>
    Metadata
    Tx ________________________________________________ tx_+KMLAfhCuEAKN05UwTV0fSgO5woziVNnAMBcDrh46XlNFTZTJQlI05fz/8pVSyrb1guCLcw8n7++O887k/JEu6/XHcCSHOMMuFv4WQwBoQEYh8aMDs7saMDBvys+lbKds3Omnzm4crYNbs9xGolBm6EBE9B4l/BeyxMO//3ANxwyT+ZHL52j9nAZosRe/YFuK4eIDeC2s6dkAACGD1WGT5gAAASAN24JGA==
    Hash ______________________________________________ th_2gAL72dtnaeDcZoZA9MbfSL1JrWzNErMJuikmTRvBY8zhkGh91
    Signature _________________________________________ sg_2LX9hnJRiYGSspzpS34QeN3PLT9bGSkFRbad9LXvLj5QUFoV5eHRf9SueDgLiiquCGbeFEBPBe7xMJidf8NMSuF16dngr
    Network id ________________________________________ ae_uat
  </spend transaction>


#. Verify the balance of the new account

::
  $ aecli inspect ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
  <account>
    Balance ___________________________________________ 1AE
    Id ________________________________________________ ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
    Kind ______________________________________________ basic
    Nonce _____________________________________________ 0
    Payable ___________________________________________ True
  </account>


