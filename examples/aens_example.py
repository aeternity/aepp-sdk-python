from aeternity.aens import Name
from aeternity.config import Config

Config.set_default(Config(local_port=3013, internal_port=3113, websocket_port=3114))

name = Name('foobar.aet')
if name.is_available():
    name.preclaim()
    name.claim_blocking()
    name.update(target='ak$deadbeef')
