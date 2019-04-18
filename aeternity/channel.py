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

    def __init__(self, channel_options):
        options_keys = {'sign', 'endpoint', 'url'}
        params = {k: channel_options[k] for k in list(channel_options.keys()) if k not in options_keys}
        url = channel_url(channel_options['url'], params, channel_options.get('endpoint', None))
        self.ws = websocket.WebSocketApp(url,
                                         on_message=handle_message,
                                         on_error=handle_error,
                                         on_close=handle_close,
                                         on_open=handle_connection
                                        )
        self.ws.run_forever()
