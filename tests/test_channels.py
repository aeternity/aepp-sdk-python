from aeternity.channel import Channel
from aeternity import transactions, signing, node, identifiers
import time
import asyncio
import pytest


@pytest.mark.asyncio
async def test_channel_connection():
    acc = signing.Account.from_keystore('/Users/shubhendu/dev/aepp-cli-js/two', '')
    tx_signer = transactions.TxSigner(
        acc,
        'ae_devnet'
    )
    opts = {
        'url': 'ws://localhost:3014',
        'role': 'initiator',
        'push_amount': 300,
        'initiator_amount': 100000000000000000,
        'responder_amount': 100000000000000000,
        'channel_reserve': 2000,
        'ttl': 10000,
        'host': 'localhost',
        'port': 3001,
        'lock_period': 1000000,
        'protocol': 'json-rpc',
        'initiator_id': 'ak_UHssTe2mXhj6LrbH6MfGQNbvn6X8YAgwjwdgefEaEB1d2HdLX',
        'responder_id': 'ak_2jgyqAtNS68QWgCej56sZpGpRrEwvUyPpL5ZbG4TeZBxByBMS8',
        'sign': tx_signer.sign_encode_transaction
    }
    channel = Channel(opts)
    await channel.create()
    

