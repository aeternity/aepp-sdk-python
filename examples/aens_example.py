from aeternity.aens import AEName
from aeternity.config import Config

Config.set_defaults(Config(external_host=3013, internal_host=3113, websocket_host=3114))

name = AEName('foobar.aet')
if name.is_available():
    name.preclaim()
    name.claim_blocking()
    name.update(target='ak_deadbeef')
