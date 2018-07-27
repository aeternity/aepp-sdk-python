import pytest
from aeternity.openapi import OpenAPICli
from aeternity.tests import NODE_URL, NODE_URL_INTERNAL, PUBLIC_KEY

client, priv_key, pub_key = None, None, None


def test_generatedcli():
    # open client
    client = OpenAPICli(NODE_URL, NODE_URL_INTERNAL)
    calls = [
        {
            "name": "get_top",
            "method": "get_top",
            "scenarios": [
                {
                    "name": "ok",
                    "params": {},
                    "wantErr": False
                }
            ]
        },
        {
            "name": "get_header_by_hash",
            "method": "get_header_by_hash",
            "scenarios": [
                {
                    "name": "err invalid hash",
                    "params": {
                      "hash": "xxxxx"
                    },
                    "wantErr": True
                },
                {
                    "name": "err missing parameter required",
                    "params": {},
                    "wantErr": True
                }
            ]
        },
        {
            "name": "get_key_block_by_height",
            "method": "get_key_block_by_height",
            "scenarios": [
                {
                    "name": "ok ",
                    "params": {
                      "height": 1
                    },
                    "wantErr": False
                },
                {
                    "name": "invalid type",
                    "params": {
                        "height": "1"
                    },
                    "wantErr": True
                },
                {
                    "name": "err missing parameter required",
                    "params": {},
                    "wantErr": True
                }
            ]
        },
        {
            "method": "get_account_balance",
            "scenarios": [
                {
                    "name": "ok",
                    "params": {
                      "address": PUBLIC_KEY
                    },
                    "wantErr": False
                },
                {
                    "name": "ok",
                    "params": {
                        "address": "xxxx"
                    },
                    "wantErr": True
                },
                {
                    "name": "err missing parameter required",
                    "params": {
                        "height": 12,
                    },
                    "wantErr": True
                }
            ]
        },
    ]

    for a in client.get_api_methods():
        print(a.name)

    for c in calls:
        for s in c.get("scenarios"):
            try:
                getattr(client, c.get("method"))(**s.get("params"))
                if s.get("wantErr"):
                    pytest.fail(f"{c.get('method')}/{s.get('name')} wantErr = {s.get('wantErr')} ")
            except Exception as e:
                if not s.get("wantErr"):
                    pytest.fail(f"{c.get('method')}/{s.get('name')} wantErr = false , got {e} ")
