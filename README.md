# aepp-sdk-python

## Introduction

This repo is for tools and notes for working with aeternity when you're running
an epoch node on your local machine.

## CLI Usage

See below for programmatic usage

You can launch the CLI tool using
```
python -m aeternity
```

Available commands:
```
aeternity cli tool:
Usage:
    aens available <domain.aet>
            Check Domain availablity
    aens register <domain.aet> [--no-input]
            Register a domain (incurs fees!)
    aens status <domain.aet>
            Checks the status of a domain
    aens update <domain.aet> <address>
            Updates where the name points to
    aens revoke <domain.aet> [--no-input]
            Removes this domain from the block chain (incurs fees!)
    aens transfer <domain.aet> <receipient_address> [--no-input]
            Transfers a domain to another user
The `--no-input` will suppress any questions before performing the action.

```

## Programmatic Usage

### Oracles

Oracles are a means to provide external data in the block chain which then
can be used in smart contracts. There are two roles when using an oracle:

 - Oracle Operator ("hosts" the oracle and responds to queries)
 - Oracle User (sends queries to the oracle)

To provide an Oracle on the block chain, you have to inherit from aeternity.Oracle
and implement `get_reply` which will be passed a `message` when a request to
this oracle was found in the block chain.

#### Oracle Operator

Furthermore you must specify `query_format`, `response_format`,
`default_query_fee`, `default_fee`, `default_query_ttl`, `default_response_ttl`

For example:
```python
from aeternity import Oracle

class WeatherOracle(Oracle):
    query_format = 'weather_query2'
    response_format = 'weather_resp2'
    default_query_fee = 4
    default_fee = 6
    default_query_ttl = 10
    default_response_ttl = 10

    def get_reply(self, message):
        return '26 C'
```

To act as operator of this oracle, you have to connect to your local epoch node
(see [the epoch repo](https://github.com/aeternity/epoch) to find out how to run
a local node), instantiate your oracle and register it on the block chain.

```python
from aeternity import Config, EpochClient
# example configuration to create a connection to your node:
config = Config(local_port=3013, internal_port=3113, websocket_port=3114)
client = EpochClient(config=config)  # connect with the epoch node
client.register_oracle(WeatherOracle())  # instantiate and register your oracle
client.run() # blocking, responds to all queries for all registered oracles
```

#### Oracle User

The oracle operator will want to publish their oracle using a description how
to talk to their oracle. All that has to be done is to create a corresponding
`OracleQuery` class. Normally it's in the interest of the oracle operator to do
this, but you can also implement this yourself:

```python
from aeternity import OracleQuery
class WeatherOracleQuery(OracleQuery):
    oracle_id = 'deadbeef...'  # query_id of the oracle as published by the operator
    query_fee = 4      # these are the same values as the Oracle
    fee = 6
    response_ttl = 10
    query_ttl = 10
    
    def on_response(self, query):
        print('You requested %s' % query)
        print('The oracle responded %s' % query)
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
weather_oracle_query = WeatherOracleQuery()
client.
``` 



### AENS (aeternity name system)

To register human-readable names with the aeternity naming system you also need
to connect to your local epoch node.

```python
from aeternity import Config, EpochClient, Name
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
oracle = WeatherOracle()
client.register_oracle(oracle)  # the oracle must be registered for this to work
name.update(target=oracle)
```

## Reference:

(AENS API Spec)[https://github.com/aeternity/protocol/blob/master/epoch/api/naming_system_api_usage.md]
(AENS Protocol)[https://github.com/aeternity/protocol/blob/master/AENS.md]


