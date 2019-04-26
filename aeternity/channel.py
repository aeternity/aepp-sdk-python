import asyncio
import json
import namedtupled
import websockets

from aeternity import defaults

CHANNELS = set()


class Channel(object):

    def __init__(self, channel_options):
        options_keys = {'sign', 'endpoint', 'url'}
        endpoint = channel_options.get('endpoint', defaults.CHANNEL_ENDPOINT)
        wsUrl = channel_options.get('url', defaults.CHANNEL_URL)
        self.sign = channel_options.get('sign', None)
        self.params = {k: channel_options[k] for k in channel_options.keys() if k not in options_keys}
        self.url = self.channel_url(wsUrl, self.params, endpoint)
        self.params = namedtupled.map(self.params)

    def create(self):
        asyncio.ensure_future(self._start_ws())

    async def _start_ws(self):
        async with websockets.connect(self.url) as websocket:
            self.ws = websocket
            await self.message_handler()

    async def message_handler(self):
        async for message in self.ws:
            print(message)
            msg = namedtupled.map(json.loads(message))
            if msg.method == f"channels.sign.{self.params.role}_sign":
                await self._sign_channel_tx(msg.params.data.tx)

    def channel_url(self, url, params, endpoint):
        param_string = '&'.join('{!s}={!r}'.format(key, val) for (key, val) in params.items())
        return f"{url}/{endpoint}?{param_string}".replace("'", "")

    async def channel_call(self, method, params):
            message = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params
            }
            print(message)
            await self.ws.send(json.dumps(message))

    def balances(self, accounts=None):
        accounts = accounts if accounts else [self.params.initiator_id, self.params.responder_id]
        asyncio.ensure_future(self.channel_call('channels.get.balances', {'accounts': accounts}))

    async def _sign_channel_tx(self, tx):
        signedTx = self.sign(tx)
        await self.channel_call(f'channels.{self.params.role}_sign', {'tx': signedTx.tx})
