# Using the command line tool to interact with æternity

## Introduction

The `aecli` command line tool is there to provide a simple way to interact with æternity. Here we give a quick introduction to its use.

## Generating a wallet

In order to do anything with æternity you'll need a wallet, and some tokens. The first step is to make yourself a wallet:
```
$ aecli wallet mywallet create
Enter the wallet password []: 
Wallet created
Wallet address________________ ak$wmZUvZWrVibPM2PuSGhgWmMQXchEWgRTbwBp7tYUcPyBYHnpR
Wallet path___________________ /home/newby/projects/aeternity/aepp-sdk-python/mywallet
$ 
```T

Next you'll need some tokens. If you don't want to mine, you'll have to get someone to transfer you some--fortunately we're here to do that. Send an email with your public key (wallet address, starting with `ak$` above) to aepp-dev@aeternity.com and we'll transfer you some tokens so you can start to interact with the public nodes.

Now you have the tokens, check your balance:

```
$ aecli -u http://localhost:3013 wallet mywallet balance
Enter the wallet password []: 
Account balance_______________ 1000
```

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
and so on. TODO: examples with transactions

```
$ aecli -u http://localhost:3013 inspect account 'ak$wmZUvZWrVibPM2PuSGhgWmMQXchEWgRTbwBp7tYUcPyBYHnpR'
Account balance_______________ 993
```

## Naming, or, I am not a number, I am a free man!

The æternity naming system allows you to register a name for your account (or oracle).

```
$ aecli -u localhost:3013 wallet mywallet name 'newby.aet' claim
Enter the wallet password []: 
Name newby.aet claimed
```

## Making a new account and transferring tokens to it

Let's make a second wallet, and give it some tokens. First, make the new wallet

```
$ aecli wallet ./secondwallet create
Enter the wallet password []: 
Wallet created
Wallet address________________ ak$gqYTvEBEivy2bk8MWYYNqXX2LvMRYho5i43YhPc6iiJNt6wwc
Wallet path___________________ /home/newby/projects/aeternity/aepp-sdk-python/secondwallet
$ aecli wallet ./secondwallet
Usage: aecli wallet [OPTIONS] [KEY_PATH] COMMAND [ARGS]...

Error: Missing command.
$ aecli wallet 
Usage: aecli wallet [OPTIONS] [KEY_PATH] COMMAND [ARGS]...

  Handle wallet operations

Options:
  --help  Show this message and exit.

Commands:
  address  Print the wallet address (public key)
  balance  Get the balance of a wallet
  create   Create a new wallet
  name     Handle name lifecycle
  save     Save a private keys string to a password...
  spend    Create a transaction to another wallet
$ aecli -u localhost:3013 wallet ./mywallet balance
Enter the wallet password []: 
No connection adapters were found for 'localhost:3013/v2/version'
$ aecli -u http://localhost:3013 wallet ./mywallet balance
Enter the wallet password []: 
Account balance_______________ 993
$ aecli -u http://localhost:3013 wallet ./mywallet spend 'ak$gqYTvEBEivy2bk8MWYYNqXX2LvMRYho5i43YhPc6iiJNt6wwc' 500
Enter the wallet password []: 
Transaction posted to the chain
Transaction hash______________ th$1N5ZXmjcyAPXfnKZoH3nuVvtWBjeuTiDMfMQpuTMhjvfcmJJV
Sender account________________ ak$wmZUvZWrVibPM2PuSGhgWmMQXchEWgRTbwBp7tYUcPyBYHnpR
Recipient account_____________ ak$gqYTvEBEivy2bk8MWYYNqXX2LvMRYho5i43YhPc6iiJNt6wwc
$ aecli -u http://localhost:3013 wallet ./mywallet balance
Enter the wallet password []: 
Account balance_______________ 993
$ aecli -u http://localhost:3013 wallet ./mywallet balance
Enter the wallet password []: 
Account balance_______________ 993
$ aecli chain top
Block hash____________________ bh$2ZTaes1v6sfVbva5sNFjwAUkM5LQj1C4WGMScQgJ8KvGzuS9D2
Block height__________________ 42809
State hash____________________ bs$ccQ93AstkCD11zKfVS3ZKt3gqnyseFNUUcAqNQQDrP8VHGYKp
Miner_________________________ ak$2gH5J6a8gif9Yx7y73WKVB9rPUYCnpTter7PiT3qu4ZfxWhDyG
Time__________________________ 2018-08-01T11:09:21.444000+00:00
Previous block hash___________ bh$2sKfDkuqJrfutjd6E5UJp6pdEBNdYsYRR8ZxLt52PqVodDoCpc
Transactions__________________ 0
$ aecli -u http://localhost:3013 chain top
Block hash____________________ bh$2QRNqZjYayRZa4mbt1TGDxqyHrGdrXXsK3XpvHrEGGNV6PZdfv
Block height__________________ 2344
State hash____________________ bs$2QNVM5uko3f8cvXSxiNoY8Ts8W5P2HGWeUrhWcs7PDKpdwebdv
Miner_________________________ ak$2rK74oqqcNwKUgswoeg5SVMhgzd8Zayo4GtMy1yFgKxuG1UkQZ
Time__________________________ 2018-08-01T11:09:07.914000+00:00
Previous block hash___________ bh$2fedqenHVsZ3fD5JFYQmR46j7suaQsz18Tneo4GXBJB4ujGjTY
Transactions__________________ 0
$ aecli -u http://localhost:3013 chain top
Block hash____________________ bh$JR2tCLHztZmHycbtMHtwQVuGzFBR3GVrXH2SjKwrL8NUs8qkL
Block height__________________ 2345
State hash____________________ bs$GHfVndrvX6XYXazKrh2573434CNvn7eeEQwyJk1oCZmWJB6Qt
Miner_________________________ ak$2rK74oqqcNwKUgswoeg5SVMhgzd8Zayo4GtMy1yFgKxuG1UkQZ
Time__________________________ 2018-08-01T11:09:40.462000+00:00
Previous block hash___________ bh$2QRNqZjYayRZa4mbt1TGDxqyHrGdrXXsK3XpvHrEGGNV6PZdfv
Transactions__________________ 0
$ aecli -u http://localhost:3013 wallet ./mywallet balance
Enter the wallet password []: 
Account balance_______________ 993
$ aecli -u http://localhost:3013 wallet ./mywallet balance
Enter the wallet password []: 
Account balance_______________ 993
$ aecli -u http://localhost:3013 wallet ./secondwallet balance
Enter the wallet password []: 
Error: Block or account not found
$ aecli -u http://localhost:3013 wallet ./mywallet spend 
Usage: aecli wallet spend [OPTIONS] RECIPIENT_ACCOUNT AMOUNT

Error: Missing argument "recipient_account".
$ aecli -u http://localhost:3013 wallet ./mywallet spend 'ak$gqYTvEBEivy2bk8MWYYNqXX2LvMRYho5i43YhPc6iiJNt6wwc' 101Enter the wallet password []: 
Transaction posted to the chain
Transaction hash______________ th$21gaWzJ34RooA2pgyPXA4xLf37BSpV9y6sx1CyqLEYKE85v6P7
Sender account________________ ak$wmZUvZWrVibPM2PuSGhgWmMQXchEWgRTbwBp7tYUcPyBYHnpR
Recipient account_____________ ak$gqYTvEBEivy2bk8MWYYNqXX2LvMRYho5i43YhPc6iiJNt6wwc
$ aecli -u http://localhost:3013 wallet ./secondwallet balance
Enter the wallet password []: 
Error: Block or account not found
$ aecli -u http://localhost:3013 wallet ./mywallet spend 'ak$gqYTvEBEivy2bk8MWYYNqXX2LvMRYho5i43YhPc6iiJNt6wwc' 101
Enter the wallet password []: 
Transaction posted to the chain
Transaction hash______________ th$2YVT5c2VznvenzFfW2PArBvEv9ic3tDgqgCr9cC6tcs5Lp6RbD
Sender account________________ ak$wmZUvZWrVibPM2PuSGhgWmMQXchEWgRTbwBp7tYUcPyBYHnpR
Recipient account_____________ ak$gqYTvEBEivy2bk8MWYYNqXX2LvMRYho5i43YhPc6iiJNt6wwc
$ 
```

