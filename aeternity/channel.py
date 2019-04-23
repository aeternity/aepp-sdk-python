import websocket
from aeternity import defaults

def handle_message(ws, message):
    print(message)

def handle_error(ws, error):
    print(error)

def handle_close(ws):
    print("closed")

def handle_connection(ws):
    print("connection open")

def channel_url(url, params, endpoint):
    param_string = '&'.join('{!s}={!r}'.format(key, val) for (key, val) in params.items())
    return f"{url}/{endpoint}?{param_string}".replace("'", "")

class Channel(object):

    def __init__(self, channel_options):
        options_keys = {'sign', 'endpoint', 'url'}
        endpoint = channel_options.get('endpoint', defaults.CHANNEL_ENDPOINT)
        wsUrl = channel_options.get('url', defaults.CHANNEL_URL)
        self.sign = channel_options.get('sign', None)
        self.params = {k: channel_options[k] for k in channel_options.keys() if k not in options_keys}
        url = channel_url(wsUrl, self.params, endpoint)
        self.ws = websocket.WebSocketApp(url,
                                         on_message=handle_message,
                                         on_error=handle_error,
                                         on_close=handle_close,
                                         on_open=handle_connection
                                        )
        self.ws.run_forever(ping_interval=11000, ping_timeout=10000)
