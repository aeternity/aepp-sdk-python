---
layout: page
title: SDK.py
navigation: 6
---

# aepp-sdk-python

## Introduction
[This repo](https://github.com/aeternity/aepp-sdk-python) is for tools and notes for working with æternity when you're running an Epoch node on your local machine.

[Follow these installation notes for a three-node linux setup with fast mining settings](https://github.com/aeternity/aepp-sdk-python/blob/master/INSTALL.md)

## Installation
The SDK required Python 3. For out of the box use, it is recommended to use
`venv` and install dependencies into it.

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Whenever you come back, don't forget to run `source venv/bin/activate`, again.

## CLI Usage
See below for programmatic usage

You can launch the command line tool using

```
./acecli
```

Available commands:

```
Usage: aecli [OPTIONS] COMMAND [ARGS]...

Options:
  --version                 Show the version and exit.
  -u, --url TEXT            Epoch node url
  -i, --url-internal TEXT
  -w, --url-websocket TEXT
  -q, --quiet               Print only results
  -v, --verbose             Print verbose data
  --help                    Show this message and exit.

Commands:
  Compile, deploy and execute contracts
  chain                           Interact with the blockchain
  inspect                         Get information on transactions, blocks,...
  name                            Handle name lifecycle
  oracle                          Interact with oracles
  wallet                          Handle wallet operations
```

## Programmatic Usage

### Oracles
Oracles are a means to provide external data in the block chain which then
can be used in smart contracts. There are two roles when using an oracle:

 - Oracle Operator ("hosts" the oracle and responds to queries)
 - Oracle User (sends queries to the oracle)

#### Oracle Operator

To provide an Oracle on the block chain, you have to inherit from
`aeternity.Oracle` and implement `get_reply` which will be passed a `message`
when a request to this oracle was found in the block chain.

Furthermore you must specify `query_format`, `response_format`,
`default_query_fee`, `default_fee`, `default_query_ttl`, `default_response_ttl`
in the oracle constructor.

For example:

```python
from aeternity import Oracle

class MyOracle(Oracle):
    def get_reply(self, message):
        return '42'

my_oracle = MyOracle(
    query_format='spec still missing',      # this will be defined later
    response_format='spec still missing',   # this will be defined later
    default_query_fee=4,
    default_fee=6,
    default_query_ttl=10,
    default_response_ttl=10,
)
```

To act as operator of this oracle, you have to connect to your local Epoch node
(see the [Epoch repo](https://github.com/aeternity/epoch) to find out how to run
a local node), instantiate your oracle and register it on the block chain using
`client.register_oracle`. Then you must constantly watch for queries on the
block chain using `client.run()`

```python
from aeternity import Config, EpochClient
# example configuration to create a connection to your node:
config = Config(local_port=3013, internal_port=3113, websocket_port=3114)
client = EpochClient(config=config)  # connect with the Epoch node
client.register_oracle(my_oracle)  # instantiate and register your oracle
client.run() # blocking, responds to all queries for all registered oracles
```

#### Oracle User
The oracle operator will want to publish their oracle using a description how
to talk to their oracle. All that has to be done is to create a corresponding
`OracleQuery` class. Normally it's in the interest of the oracle operator
provide this for you, but you can also easily implement this yourself in the
case that the operator did not.

```python
from aeternity import OracleQuery

class MyOracleQuery(OracleQuery):
    def on_response(self, query):
        print('You requested %s' % query)
        print('The oracle responded %s' % query)

my_query = MyOracleQuery(
    oracle_pubkey='ok$deadbeef...',  # oracle id as published by the operator
    query_fee=4,      # these are the same values as the Oracle
    fee=6,
    response_ttl=10,
    query_ttl=10,
)
```

As you can see this is mostly equivalent to the Oracle itself, but the oracle
operator may use another programming language or choose not to publish her
source, so the `Oracle` and the `OracleQuery` remain two different concepts.

Querying the oracle:

```python
from aeternity import Config, EpochClient
# example configuration to create a connection to your local node:
config = Config(local_port=3013, internal_port=3113, websocket_port=3114)
client = EpochClient(config=config)
# instantiate your oracle query and register it with the node
client.mount(my_query)
my_query.query('The answer to life, the universe and everything')
```

### AENS (æternity name system)
To register human-readable names with the æternity naming system you also need
to connect to your local Epoch node.

```python
from aeternity import Config, EpochClient, AEName
import sys
# create connection with the local node:
config = Config(local_port=3013, internal_port=3113, websocket_port=3114)
client = EpochClient(config=config)

# try registering 'example.aet' on the block chain:
name = Name(domain='example.aet')
if not name.is_available():
    print('Name is not available anymore!')
    sys.exit(1)

name.preclaim()  # preclaim will mark the domain as yours in the current block
name.claim_blocking()  # will wait for the next block to claim the domain
name.update(target='ak$1234deadbeef')  # set what this domain stands for
```

you can also pass an oracle instance directly to in the `target` parameter
when calling `update`

```python
oracle = MyOracle()
client.register_oracle(oracle)  # the oracle must be registered for this to work
name.update(target=oracle)
```

## Reference:
[AENS API Spec](https://github.com/aeternity/protocol/blob/master/epoch/api/naming_system_api_usage.md)

[AENS Protocol](https://github.com/aeternity/protocol/blob/master/AENS.md)
