# Utilities built in in the Python SDK

The scope of this page is to list some of the utilities built-in the Python SDK

## Transactions

The section covers the utilities related to transaction management.

### Compute a transaction hash

In the Æternity blockchain the transaction hashes are deterministic and can be
computed without interacting with a node.

The following is a code snippet about how to compute a transaction hash:

```python

from aeternity.transactions import TxBuilder
from aeternity.node import NodeClient, Config # we need this to retrieve the transaction

# The TxBuilder object is the one that is responsible to
# compose, encode and decode transactions

# let's get as example the transaction th_UDARRXdLrgGyzZsvKrkzo3i51x6gRdfjpbKxjA5dDHSjdBaEr
# you can get the details from https://sdk-mainnet.aepps.com/v2/transactions/th_UDARRXdLrgGyzZsvKrkzo3i51x6gRdfjpbKxjA5dDHSjdBaEr

x = {
  "block_hash":"mh_2ALC3nX5Hm9488yhPKn65egU6KWugMnAyhYiBq3eRVn9Bf2mD1","block_height":123003,"hash":"th_UDARRXdLrgGyzZsvKrkzo3i51x6gRdfjpbKxjA5dDHSjdBaEr","signatures":["sg_HPuAmqhiY84sKbQp8LiDSjH7yYiTubdVkPYewftBihaTLcAzDyY4EwRW8m6nsaLHtZN4GkBs3LtjWyKRWZybUocuwREHe"],"tx":{"amount":1000000000000000000,"fee":16820000000000,"nonce":11,"payload":"ba_Xfbg4g==","recipient_id":"ak_VcWJxsExtNwwe46junXTq8CpcNuhfxFKsaqWm5CGJuqqCAjTJ","sender_id":"ak_u2gFpRN5nABqfqb5Q3BkuHCf8c7ytcmqovZ6VyKwxmVNE5jqa","type":"SpendTx","version":1}}

tx_hash = "th_UDARRXdLrgGyzZsvKrkzo3i51x6gRdfjpbKxjA5dDHSjdBaEr"

n = NodeClient(Config(external_url="https://sdk-mainnet.aepps.com"))
# the get_transaction from the node will retrieve the transaction
# from the api and build a TxObject for us
tx = n.get_transaction(hash=tx_hash)

# the TxObject contains the calculated hash
tx.hash






```
