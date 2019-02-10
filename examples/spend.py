from aeternity.node import NodeClient
from aeternity.config import Config

import sys

Config.set_defaults(Config(external_host=3013, internal_host=3113, websocket_host=3114))

recipient, amount = sys.argv[1:3]

amount = int(amount)

node = NodeClient()

node.spend(recipient, amount)
