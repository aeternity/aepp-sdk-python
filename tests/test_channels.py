from aeternity.channel import Channel

def test_channel_connection():
    opts = {
        'url': 'ws://localhost:3014',
        'role': 'initiator',
        'push_amount': 3,
        'initiator_amount': 10,
        'responder_amount': 10,
        'channel_reserve': 2,
        'ttl': 10000,
        'host': 'localhost',
        'port': 3001,
        'lock_period': 100,
        'initiator_id': 'ak_8wWs1j2vhgjexQmKfgEBrG8ysAucRJdb3jsag3PJKjEeXswb7',
        'responder_id': 'ak_bmtGbfP3SdPoJNZCQGjjzbKRje15J9CEcWYaL1gZyv2qEyiMe'
    }
    Channel(opts)

