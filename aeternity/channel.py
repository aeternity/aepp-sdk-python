import asyncio
import websocket


def handle_message(ws, message):
    print(message)


def handle_error(ws, error):
    print(error)


def handle_close(ws):
    print("closed")

def handle_connection(ws):
    print("connection open")


def channel_url(url, params, endpoint):
    endpoint = endpoint or 'channel'
    param_string = '&'.join('{!s}={!r}'.format(key, val) for (key, val) in params.items())
    return f"{url}/{endpoint}?{param_string}".replace("'", "")

class Channel(object):
    @classmethod
    async def create(cls, channel_options):
        self = Channel()
        options_keys = {'sign', 'endpoint', 'url'}
        print(channel_options)
        params = {k: channel_options[k] for k in list(channel_options.keys()) if k not in options_keys}
        url = channel_url(channel_options['url'], params, channel_options.get('endpoint', None))
        print(url)
        self.ws = websocket.WebSocketApp(url,
                                         on_message=handle_message,
                                         on_error=handle_error,
                                         on_close=handle_close,
                                         on_open=handle_connection
                                        )
        self.ws.run_forever()
        return self


async def main():
    opts = {
        'url': 'ws://localhost:3014',
        'push_amount': 3,
        'initiator_amount': 10,
        'responder_amount': 10,
        'channel_reserve': 2,
        'ttl': 1000,
        'host': 'localhost',
        'port': 3001,
        'lockPeriod': 10,
        'initiator_id': 'ak_8wWs1j2vhgjexQmKfgEBrG8ysAucRJdb3jsag3PJKjEeXswb7',
        'responderI_id': 'ak_bmtGbfP3SdPoJNZCQGjjzbKRje15J9CEcWYaL1gZyv2qEyiMe'
    }
    channel = await Channel.create(opts)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
