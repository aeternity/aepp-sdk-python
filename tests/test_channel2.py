from aeternity.channel import Channel
from aeternity import transactions, signing
import asyncio


def test_channel_connection():
    acc2 = signing.Account.from_keystore('/Users/shubhendu/dev/aepp-cli-js/one', '')
    tx_signer2 = transactions.TxSigner(
        acc2,
        'ae_devnet'
    )
    opts2 = {
        'url': 'ws://localhost:3014',
        'role': 'responder',
        'push_amount': 3,
        'initiator_amount': 100000000000000000,
        'responder_amount': 100000000000000000,
        'channel_reserve': 2,
        'ttl': 10000,
        'host': 'localhost',
        'port': 3001,
        'lock_period': 1000000,
        'protocol': 'json-rpc',
        'initiator_id': 'ak_UHssTe2mXhj6LrbH6MfGQNbvn6X8YAgwjwdgefEaEB1d2HdLX',
        'responder_id': 'ak_2jgyqAtNS68QWgCej56sZpGpRrEwvUyPpL5ZbG4TeZBxByBMS8',
        'sign': tx_signer2.sign_encode_transaction
    }
    loop = asyncio.get_event_loop()
    channel2 = Channel(opts2)
    channel2.create()
    loop.run_forever()
