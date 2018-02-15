from aeternity.epoch import EpochClient
from aeternity.config import Config

import sys

Config.set_default(Config(local_port=3013, internal_port=3113, websocket_port=3114))

recipient, amount = sys.argv[1:3]

epoch = EpochClient()

epoch.spend(recipient, amount)

