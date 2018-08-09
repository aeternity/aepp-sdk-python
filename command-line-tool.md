# Using the command line tool to interact with æternity

## Introduction

All of our SDKs will ultimately feature an identical command line tool which provides a simple way to interact with æternity. Here we give a quick introduction to its use in the Python SDK. Here we show how it's used with the main sdk testnet, so you don't need to run your own node. If you want to do that then just modify the environment variable `EPOCH_URL` to point at your own node.

## Setting up

The instructions for setting up the aecli are in the Python SDK release notes. From here on in we'll assume that you've gone through the steps there, and have put the location of `aecli` into your `PATH` variable.

export the location of the sdk-testnet node like this:
```
export EPOCH_URL='https://sdk-testnet.aepps.com'
```

## Generating a wallet

In order to do anything with æternity you'll need a wallet, and some tokens. The first step is to make yourself a wallet, called `mywallet`:
```
$ aecli wallet mywallet create
Enter the wallet password []: 
Wallet created
Wallet address________________ ak$wmZUvZWrVibPM2PuSGhgWmMQXchEWgRTbwBp7tYUcPyBYHnpR
Wallet path___________________ /home/newby/projects/aeternity/aepp-sdk-python/mywallet
$ 
```

Note that we don't set a password on any of the wallets in this example.

Next you'll need some tokens. We've set up a web page at http://XXXXXXXXXXX which you can use to transfer yourself tokens, 250 at a time. Go there now and give yourself some tokens. 

Now you have transferred yourself tokens, check your balance:

```
$ aecli wallet mywallet balance
Enter the wallet password []: 
Account balance_______________ 1000
```

Remember that you may have to wait a short while for the tokens to show up.

Assuming all went well, you are now in a position to use all of æternity's features. Even if not, you can still inspect the blockchain.

## Looking at the chain

First, take a look at the head of the chain:
```
$ aecli chain top
Block hash____________________ bh$zy7w2hLc7rYk7vLkc4YibErtJZitTrp1CBha2s9mAkKRBxr4h
Block height__________________ 42640
State hash____________________ bs$2XAzdJyzruidUbLDwUxcWViCKxXvV7jnBqrKywjcYUtf4sz55U
Miner_________________________ ak$RTWrYQGzdq6bXEPsFn1PJp5SDBvkMNoDFxuCMwhk2t48XTdFx
Time__________________________ 2018-08-01T10:23:59.714000+00:00
Previous block hash___________ bh$srwLRbwLLzuFWnXAvd4nEHSHoVZcTPGd1VFbjwKMSwNyMCJdf
Transactions__________________ 0
$
```

From the previous block hash we can go backward through the chain:
```
$ aecli inspect block 'bh$srwLRbwLLzuFWnXAvd4nEHSHoVZcTPGd1VFbjwKMSwNyMCJdf'
Block hash____________________ bh$srwLRbwLLzuFWnXAvd4nEHSHoVZcTPGd1VFbjwKMSwNyMCJdf
Block height__________________ 42639
State hash____________________ bs$2jNh89QB4167f7v5qnB2n9JWvb1m6787gyvkZjaUK6L4EGjJux
Miner_________________________ ak$RTWrYQGzdq6bXEPsFn1PJp5SDBvkMNoDFxuCMwhk2t48XTdFx
Time__________________________ 2018-08-01T10:23:57.985000+00:00
Previous block hash___________ bh$2oD2EdZrSdcnSu7vGbaH9wHf9g8WTSuqnDk9RxB2tVRU42kvXS
Transactions__________________ 0
$ aecli inspect block 'bh$2oD2EdZrSdcnSu7vGbaH9wHf9g8WTSuqnDk9RxB2tVRU42kvXS'
Block hash____________________ bh$2oD2EdZrSdcnSu7vGbaH9wHf9g8WTSuqnDk9RxB2tVRU42kvXS
Block height__________________ 42638
State hash____________________ bs$2iPSkLFEQHKagpiFMemm5W2vNXCagbbSKtdAmG5vz51PBr3YXb
Miner_________________________ ak$2gH5J6a8gif9Yx7y73WKVB9rPUYCnpTter7PiT3qu4ZfxWhDyG
Time__________________________ 2018-08-01T10:23:52.290000+00:00
Previous block hash___________ bh$2NmrYNBUXYyvYVZEHNkS8qCsXmdBtaEXPUt15B2SPf3reS7F8S
Transactions__________________ 0
$ 
```
and so on. We can even watch the chain in real time with the `play` command:
```
$ aecli chain play
 >>>>> 
Block hash____________________ bh$LKALmVkVaqJyqSv9JnYWwDh9QCf8LbbpXyYarB8vP5TqJ4bvL
Block height__________________ 86223
State hash____________________ bs$yAd7PuriwAUqwLexYuLxLqAA5aNcdiAU3Sdou4eYBdbVVkAW1
Miner_________________________ ak$BpwWtzwJpfGe6AmusjQ9a5aqKF784nXkB2apoHPmNmrJTnPdn
Time__________________________ 2018-08-09T11:33:15.866000+00:00
Previous block hash___________ bh$NnH3UUz2J7LoWdUZi9A1p3KYTtzXeQJ2tQQB2yUnkhU3gj3rv
Transactions__________________ 0
 >>>>> 
Block hash____________________ bh$NnH3UUz2J7LoWdUZi9A1p3KYTtzXeQJ2tQQB2yUnkhU3gj3rv
Block height__________________ 86222
State hash____________________ bs$bPGmETN5kNt9cTCUbGjyAJ7wDYkCvgFz9V6xGQ8k3w1SpG9aR
Miner_________________________ ak$289g2REG4ZoavYGWhgz2p2Wq6FVXnsPurgM8UEe2UdXNXz5CXf
Time__________________________ 2018-08-09T11:33:11.853000+00:00
Previous block hash___________ bh$2jvmSTG1uZMwhaCW8J8Ug1Ddoy4EuQmzBFFeCDhs3CZDG8zuSW
Transactions__________________ 0
```
(and so on).

## Naming, or, I am not a number, I am a free man!

The æternity naming system allows you to register a name for your account (or oracle).

```

```
$ aecli -u localhost:3013 wallet mywallet name 'newby.aet' claim
Enter the wallet password []: 
Name newby.aet claimed
Transaction hash______________ th$vmucE7sFSc8QjWBAJwkh2drN3jKwtSd7KYtYzjL6Bfg1x8kyq
```

Let's inspect the transaction:

```
$ aecli inspect transaction 'th$vmucE7sFSc8QjWBAJwkh2drN3jKwtSd7KYtYzjL6Bfg1x8kyq'
Block hash____________________ bh$2nvF8jTk9aPZoq3YzaYhGhMuXL8FxptvKpyZ2p73Bjb5EAjtYH
Block height__________________ 86229
Signatures____________________ ['sg$GfYm6uBp8bGpghAptWReqb3cX6kyRQzSZdLh74LzKKtyoTninWpvhs6JMAo1CiTDmi5E7A3b2ztC3beBq3sMVoprmxRCC']
Sender account________________ None
Recipient account_____________ None
Amount________________________ None
TTL___________________________ 86238
```

and check out the name we registered, to ensure we have it:

```
$ aecli inspect name newby.aet
Status________________________ CLAIMED
Pointers______________________ {'account_pubkey': 'ak$wmZUvZWrVibPM2PuSGhgWmMQXchEWgRTbwBp7tYUcPyBYHnpR'}
TTL___________________________ 86329
```

## Making a new account and transferring tokens to it

Let's make a second wallet, and give it some tokens. First, make the new wallet

```
$ aecli wallet ./secondwallet create
Enter the wallet password []: 
Wallet created
Wallet address________________ ak$gqYTvEBEivy2bk8MWYYNqXX2LvMRYho5i43YhPc6iiJNt6wwc
Wallet path___________________ /home/newby/projects/aeternity/aepp-sdk-python/secondwallet
$ aecli wallet secondwallet balance
Enter the wallet password []: 
Error: Block or account not found
$ aecli wallet mywallet spend 'ak$2MgcVUMneuZshmoMkNKuWqsa1GhakSKoBFhe37crpuVAWcYtRA' 125
Enter the wallet password []: 
Transaction posted to the chain
Transaction hash______________ th$29hPH2jNrZu1kfdmNhE991GaXzRD2QfJGek3xaXVbJZJWGsfQ2
Sender account________________ ak$wmZUvZWrVibPM2PuSGhgWmMQXchEWgRTbwBp7tYUcPyBYHnpR
Recipient account_____________ ak$2MgcVUMneuZshmoMkNKuWqsa1GhakSKoBFhe37crpuVAWcYtRA
$ aecli wallet secondwallet balance
Enter the wallet password []: 
Account balance_______________ 125
```

