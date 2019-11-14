#!/usr/bin/env python
import argparse
import json
from aeternity.signing import Account

"""
Example app to deal with common dev issues:
- export secret/public key from a keystore
- generate a number of accounts to be used
"""

# max number of account to generate
MAX_N_ACCOUNTS = 1000

def cmd_export(args):
    try:
        a = Account.from_keystore(args.keystore_path, args.password)
        print(json.dumps(
            {
                "keystore": args.keystore_path,
                "secret_key": a.get_secret_key(),
                "address": a.get_address()
            }, indent=2))
    except Exception as e:
        print(f"Invalid keystore or password: {e}")

def cmd_generate(args):
    try:
        if args.n > MAX_N_ACCOUNTS:
            print(f"Max number of accounts to generate is {MAX_N_ACCOUNTS}, requested: {args.n}")
        accounts = []
        for i in range(args.n):
            a = Account.generate()
            accounts.append({
                "index": i,
                "secret_key": a.get_secret_key(),
                "address": a.get_address()
            })
        print(json.dumps(accounts, indent=2))
    except Exception as e:
        print(f"Generation error: {e}")


if __name__ == "__main__":
    commands = [
        {
            'name': 'export',
            'help': 'export the secret/public key of a encrypted keystore as plain text WARNING! THIS IS UNSAFE, USE FOR DEV ONLY',
            'target': cmd_export,
            'opts': [
                {
                    "names": ["keystore_path"],
                    "help": "the keystore to use export",
                },
                {
                    "names": ["-p", "--password"],
                    "help": "the keystore password (default blank)",
                    "default": ""
                }
            ]
        },
        {
            'name': 'generate',
            'help': 'generate one or more accounts and print them on the stdout',
            'target': cmd_generate,
            'opts': [
                {
                    "names": ["-n"],
                    "help": "number of accounts to generate (default 10)",
                    "default": 10,
                }
            ]
        }
    ]
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True
    subparsers.dest = 'command'
    # register all the commands
    for c in commands:
        subparser = subparsers.add_parser(c['name'], help=c['help'])
        subparser.set_defaults(func=c['target'])
        # add the sub arguments
        for sa in c.get('opts', []):
            subparser.add_argument(*sa['names'],
                                   help=sa['help'],
                                   action=sa.get('action'),
                                   default=sa.get('default'))

    # parse the arguments
    args = parser.parse_args()
    # call the function
    args.func(args)
