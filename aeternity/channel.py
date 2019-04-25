import websockets
import json
import namedtupled
from aeternity import defaults

CHANNELS = set()

class Channel(object):

    sequence = 0

    def __init__(self, channel_options):
        options_keys = {'sign', 'endpoint', 'url'}
        endpoint = channel_options.get('endpoint', defaults.CHANNEL_ENDPOINT)
        wsUrl = channel_options.get('url', defaults.CHANNEL_URL)
        self.sign = channel_options.get('sign', None) 
        self.params = {k: channel_options[k] for k in channel_options.keys() if k not in options_keys}
        self.url = self.channel_url(wsUrl, self.params, endpoint)
        self.params = namedtupled.map(self.params)

    async def create(self):
        async with websockets.connect(self.url) as websocket:
            self.ws = websocket
            await self.message_handler()

    async def message_handler(self):
        async for message in self.ws:
            print(message)
            msg = json.loads(message)
            if msg["method"] == "channels.sign.initiator_sign":
                signed = self.sign(msg["params"]["data"]["tx"])
                print(signed)
                await self.channel_call('channels.initiator_sign', self.sequence, {'tx': signed.tx})

    def channel_url(self, url, params, endpoint):
        param_string = '&'.join('{!s}={!r}'.format(key, val) for (key, val) in params.items())
        return f"{url}/{endpoint}?{param_string}".replace("'", "")

    async def channel_call(self, method, id, params):
            message = {
                "jsonrpc": "2.0",
                "id": id,
                "method": method,
                "params": params
            }
            print(message)
            await self.ws.send(json.dumps(message))

    async def balances(self, accounts=None):
        accounts = accounts if accounts else [self.params['initiator_id'], self.params['responder_id']]
        await self.channel_call('channels.get.balances', self.sequence, {'accounts': accounts})
        self.increment_sequence()

    def increment_sequence(self):
        self.sequence += 1
