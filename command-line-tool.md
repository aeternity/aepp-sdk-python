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
```

Next you'll need some tokens. If you don't want to mine, you'll have to get someone to transfer you some--fortunately we're here to do that. Send an email with your public key (wallet address, starting with `ak$` above) to aepp-dev@aeternity.com and we'll transfer you some tokens so you can start to interact with the public nodes.

