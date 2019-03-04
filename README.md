---
layout: page
title: SDK.py
navigation: 6
---

# aepp-sdk-python

## Introduction

[This repo](https://github.com/aeternity/aepp-sdk-python) is for developing apps for the æternity blockchain in Python. Please see the [main dev site](https://dev.aepps.com) for instructions on accessing the testnet, and for running a local æternity node.

## Installation

The SDK required Python 3. For out of the box use, it is recommended to use
`venv` and install dependencies into it.

```
python3 -m venv venv
source venv/bin/activate
pip install aepp-sdk
```

Whenever you come back, don't forget to run `source venv/bin/activate`, again.

## CLI Usage

See below for programmatic usage

You can launch the command line tool using

```
./aecli
```

Available commands:

```
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
```

## Environment variables

Use the environment variables

- `NODE_URL`
- `NODE_URL_DEBUG`

### Example usage

The following is a walkthrough to execute an offline spend transaction on the *testnet* network

1. Set the environment variables
```
export NODE_URL=https://sdk-testnet.aepps.com
```

❗ When not set the command line client will connect to mainnet

2. Retrieve the top block
```
$ aecli chain top
<top for node at https://sdk-testnet.aepps.com >
  Beneficiary _______________________________________ ak_2iBPH7HUz3cSDVEUWiHg76MZJ6tZooVNBmmxcgVK6VV8KAE688
  Hash ______________________________________________ kh_WTqMQQRsvmbtP5yrKPxd4p2PPKiA51AuPyCkVJk7d7HVtkhS6
  Height ____________________________________________ 46049
  Info ______________________________________________ cb_Xfbg4g==
  Miner _____________________________________________ ak_24yQXT3g2jNryZbY2veHYcgQn3PspfTnkTHbXMwNYDQd9NZAs5
  Nonce _____________________________________________ 17848795956567990671
  Prev hash _________________________________________ kh_B5Q3F7Gxbmg2z3prkay2uYohvhv4xXUKQzKKkbTdm7Z3GuQxU
  Prev key hash _____________________________________ kh_B5Q3F7Gxbmg2z3prkay2uYohvhv4xXUKQzKKkbTdm7Z3GuQxU
  State hash ________________________________________ bs_bkP3QdFKCWNetDHfwL3rJG2hEgRzZRAQN6jh33SKwUd17tBjp
  Target ____________________________________________ 538409724
  Time ______________________________________________ 2019-03-03T23:38:49.720000+00:00
  Version ___________________________________________ 2
</top for node at https://sdk-testnet.aepps.com >
```

3. Create a new account

```
aecli account create Bob.json
Enter the account password []:
<account>
  Address ___________________________________________ ak_BobY97QUVR4iDLg4k3RKmy6shZYx9FR75nLaN33GsVmSnhWxn
  Path ______________________________________________ /.../Bob.json
</account>

```

❗ Make sure that you use a long and difficult-to-guess password for an account that you plan to use on mainnet

4. Go to [testnet.faucet.aepps.com](https://testnet.faucet.aepps.com) and top up your account

![](docs/assets/images/faucet.png)

5. Inspect the transaction reported by the faucet app
```
aecli inspect th_2CV4a7xxDYj5ysaDjXNoCSLxnkowGM5bbyAvtdoPvHZwTSYykX
<transaction>
  Block hash ________________________________________ mh_2Kw9ktNiU36uFC2Fs2FZtpFfok6GQZTt5rY6Vs5bS6jNBw6bzd
  Block height ______________________________________ 46052
  Hash ______________________________________________ th_2DWDxx2egaF887S4M7GGBWsEGqkQvPYcXsvJzqapd6CRLGKobJ
  <signatures 1>
    Signature #1 ____________________________________ sg_CotVHb914KqZpSETmY4mWhpFpCCUdCJssYbJHx1iR6S94SrDPfTyqUfqQkoBW4dVSgU1kfFUJC9yc6sUaHSte2xBvCKzR
  <tx>
    Amount __________________________________________ 5000000000000000000
    Fee _____________________________________________ 20000000000000
    Nonce ___________________________________________ 1059
    Payload _________________________________________ Faucet Tx
    Recipient id ____________________________________ ak_BobY97QUVR4iDLg4k3RKmy6shZYx9FR75nLaN33GsVmSnhWxn
    Sender id _______________________________________ ak_2iBPH7HUz3cSDVEUWiHg76MZJ6tZooVNBmmxcgVK6VV8KAE688
    Ttl _____________________________________________ 46102
    Type ____________________________________________ SpendTx
    Version _________________________________________ 1
  </tx>
</transaction>
```

6. Create another account

```
aecli account create Alice.json
Enter the account password []:
<account>
  Address ___________________________________________ ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
  Path ______________________________________________ /.../Alice.json
</account>
```


7. Transfer some tokens to an account to the other

```
aecli account spend Bob.json ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M 1000000000000000000
Enter the account password []:
<spend transaction>
  <data>
    Tag _____________________________________________ 12
    Vsn _____________________________________________ 1
    Sender id _______________________________________ ak_BobY97QUVR4iDLg4k3RKmy6shZYx9FR75nLaN33GsVmSnhWxn
    Recipient id ____________________________________ ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
    Amount __________________________________________ 1000000000000000000
    Fee _____________________________________________ 16860000000000
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
```

8. Verify the balance of the new account
```
aecli inspect ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
<account>
  Balance ___________________________________________ 1000000000000000000
  Id ________________________________________________ ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
  Nonce _____________________________________________ 0
</account>
```



## Advanced usage

For advanced usage check the [documentation](docs).


## Reference:

[AENS API Spec](https://github.com/aeternity/protocol/blob/master/node/api/naming_system_api_usage.md)

[AENS Protocol](https://github.com/aeternity/protocol/blob/master/AENS.md)
