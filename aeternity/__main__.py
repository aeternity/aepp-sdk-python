import logging
import click
import os
import json
import sys

from aeternity import __version__

from aeternity.epoch import EpochClient
from aeternity.config import Config, MAX_TX_TTL, ConfigException, UnsupportedEpochVersion
# from aeternity.oracle import Oracle, OracleQuery, NoOracleResponse
from aeternity.signing import Account
from aeternity.contract import Contract
from aeternity.aens import AEName

from datetime import datetime, timezone


logging.basicConfig(format='%(message)s', level=logging.INFO)


CTX_EPOCH_URL = 'EPOCH_URL'
CTX_EPOCH_URL_INTERNAL = 'EPOCH_URL_INTERNAL'
CTX_EPOCH_URL_WEBSOCKET = 'EPOCH_URL_WEBSOCKET'
CTX_KEY_PATH = 'KEY_PATH'
CTX_VERBOSE = 'VERBOSE'
CTX_QUIET = 'QUIET'
CTX_AET_DOMAIN = 'AET_NAME'
CTX_FORCE_COMPATIBILITY = 'CTX_FORCE_COMPATIBILITY'
CTX_BLOCKING_MODE = 'CTX_BLOCKING_MODE'
CTX_OUTPUT_JSON = 'CTX_OUTPUT_JSON'


def _epoch_cli():
    try:
        ctx = click.get_current_context()
        # set the default configuration
        Config.set_defaults(Config(
            external_url=ctx.obj.get(CTX_EPOCH_URL),
            internal_url=ctx.obj.get(CTX_EPOCH_URL_INTERNAL),
            websocket_url=ctx.obj.get(CTX_EPOCH_URL_WEBSOCKET),
            force_comaptibility=ctx.obj.get(CTX_FORCE_COMPATIBILITY)
        ))
    except ConfigException as e:
        print("Configuration error: ", e)
        exit(1)
    except UnsupportedEpochVersion as e:
        print(e)
        exit(1)

    # load the epoch client
    return EpochClient(blocking_mode=ctx.obj.get(CTX_BLOCKING_MODE))


def _account(password=None):
    """
    utility function to get the keypair from the click context
    :return: (keypair, keypath)
    """
    ctx = click.get_current_context()
    kf = ctx.obj.get(CTX_KEY_PATH)
    if not os.path.exists(kf):
        print(f'Key file {kf} does not exits.')
        exit(1)
    try:
        if password is None:
            password = click.prompt("Enter the account password", default='', hide_input=True)
        return Account.read_from_private_key(kf, password), os.path.abspath(kf)
    except Exception:
        print("Invalid password")
        exit(1)


def _check_prefix(data, prefix):
    """
    helper method to check the validity of a prefix
    """

    if len(data) < 3:
        print(f"Invalid input: '{data}'")
        exit(1)

    if not data.startswith(f"{prefix}_"):
        if prefix == 'ak':
            print("Invalid account address, it shoudld be like: ak_....")
        if prefix == 'th':
            print("Invalid transaction hash, it shoudld be like: th_....")
        if prefix in ('bh', 'kh'):
            print("Invalid block hash, it shoudld be like: bh_...., kh_...")
        exit(1)


def _verbose():
    """tell if the command has the verbose flag"""
    ctx = click.get_current_context()
    return ctx.obj.get(CTX_VERBOSE, False)


def _po(label, value, offset=0):
    """
    pretty printer
    :param data: single enty or list of key-value tuples
    :param title: optional title
    :param quiet: if true print only the values
    """
    if isinstance(value, dict):
        o = offset + 1
        for k, v in value.items():
            _po(k, v, o)
    elif isinstance(value, tuple):
        o = offset + 1
        for k, v in value._asdict().items():
            _po(k, v, o)
    elif isinstance(value, list):
        _po(label, ', '.join(value), offset)
    else:
        lo = " " * offset
        lj = 53 - len(lo)
        if label == "Time":
            value = datetime.fromtimestamp(value / 1000, timezone.utc).isoformat('T')
        print(f"{lo}{label.ljust(lj, '_')} {value}")


def _print_object(data, title=None):
    ctx = click.get_current_context()

    if ctx.obj.get(CTX_OUTPUT_JSON, False):
        if isinstance(data, tuple):
            print(json.dumps(data._asdict(), indent=2))
            return

        print(json.dumps(data, indent=2))
        return

    if title is not None:
        print(title)
    _po(title, data)


# Commands
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# the priority for the url selection is PARAM, ENV, DEFAULT


@click.group()
@click.pass_context
@click.version_option()
@click.option('--url', '-u', default='https://sdk-testnet.aepps.com', envvar='EPOCH_URL', help='Epoch node url', metavar='URL')
@click.option('--url-internal', '-i', default='https://sdk-testnet.aepps.com/internal', envvar='EPOCH_URL_INTERNAL', metavar='URL')
@click.option('--url-websocket', '-w', default='ws://sdk-testnet.aepps.com', envvar='EPOCH_URL_WEBSOCKET', metavar='URL')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Print verbose data')
@click.option('--force', '-f', is_flag=True, default=False, help='Ignore epoch version compatibility check')
@click.option('--wait', is_flag=True, default=False, help='Wait for a transaction to be included in the chain before returning')
@click.option('--json', 'json_', is_flag=True, default=False, help='Print output in JSON format')
@click.version_option(version=__version__)
def cli(ctx, url, url_internal, url_websocket, verbose, force, wait, json_):
    """
    Welcome to the aecli client.

    The client is to interact with an epoch node.

    """
    ctx.obj[CTX_EPOCH_URL] = url
    ctx.obj[CTX_EPOCH_URL_INTERNAL] = url_internal
    ctx.obj[CTX_EPOCH_URL_WEBSOCKET] = url_websocket
    ctx.obj[CTX_VERBOSE] = verbose
    ctx.obj[CTX_FORCE_COMPATIBILITY] = force
    ctx.obj[CTX_BLOCKING_MODE] = wait
    ctx.obj[CTX_OUTPUT_JSON] = json_


@cli.command('config', help="Print the client configuration")
@click.pass_context
def config(ctx):
    _print_object({
        "Epoch URL": ctx.obj.get(CTX_EPOCH_URL),
        "Epoch internal URL": ctx.obj.get(CTX_EPOCH_URL_INTERNAL, 'N/A'),
        "Epoch websocket URL": ctx.obj.get(CTX_EPOCH_URL_WEBSOCKET, 'N/A'),
    }, title="aecli settings")


#        _                                               _
#       / \                                             / |_
#      / _ \     .---.  .---.   .--.   __   _   _ .--. `| |-'.--.
#     / ___ \   / /'`\]/ /'`\]/ .'`\ \[  | | | [ `.-. | | | ( (`\]
#   _/ /   \ \_ | \__. | \__. | \__. | | \_/ |, | | | | | |, `'.'.
#  |____| |____|'.___.''.___.' '.__.'  '.__.'_/[___||__]\__/[\__) )
#


@cli.group(help="Handle account operations")
@click.pass_context
@click.argument('key_path', default='sign_key', envvar='WALLET_SIGN_KEY_PATH')
def account(ctx, key_path):
    ctx.obj[CTX_KEY_PATH] = key_path


@account.command('create', help="Create a new account")
@click.pass_context
@click.option('--password', default=None, help="Set a password from the command line [WARN: this method is not secure]")
@click.option('--force', default=False, is_flag=True, help="Overwrite exising keys without asking")
def account_create(ctx, password, force):
    kp = Account.generate()
    kf = ctx.obj.get(CTX_KEY_PATH)
    if not force and os.path.exists(kf):
        click.confirm(f'Key file {kf} already exists, overwrite?', abort=True)
    if password is None:
        password = click.prompt("Enter the account password", default='', hide_input=True)
    kp.save_to_file(kf, password)
    _print_object({
        'Account address': kp.get_address(),
        'Account path': os.path.abspath(kf)
    }, title='Account created')


@account.command('save', help='Save a private keys string to a password protected file account')
@click.argument("private_key")
@click.pass_context
def account_save(ctx, private_key):
    try:
        kp = Account.from_private_key_string(private_key)
        kf = ctx.obj.get(CTX_KEY_PATH)
        if os.path.exists(kf):
            click.confirm(f'Key file {kf} already exists, overwrite?', abort=True)
        password = click.prompt("Enter the account password", default='', hide_input=True)
        kp.save_to_file(kf, password)
        _print_object({
            'Account address': kp.get_address(),
            'Account path': os.path.abspath(kf)
        }, title='Account saved')
    except Exception as e:
        print(e)


@account.command('address', help="Print the account address (public key)")
@click.option('--password', default=None, help="Read the password from the command line [WARN: this method is not secure]")
@click.option('--private-key', is_flag=True, help="Print the private key instead of the account address")
def account_address(password, private_key):
    kp, kf = _account(password=password)
    o = {
        'Account address': kp.get_address()
    }
    if private_key:
        o["Private key"] = kp.get_private_key()
    _print_object(o)


@account.command('balance', help="Get the balance of a account")
@click.option('--password', default=None, help="Read the password from the command line [WARN: this method is not secure]")
def account_balance(password):
    kp, _ = _account(password=password)

    try:
        account = _epoch_cli().get_account_by_pubkey(pubkey=kp.get_address())
        _print_object({"Account balance": account.balance})
    except Exception as e:
        print(e)


@account.command('spend', help="Create a transaction to another account")
@click.argument('recipient_account', required=True)
@click.argument('amount', required=True, default=1)
@click.option('--ttl', default=MAX_TX_TTL, help="Validity of the spend transaction in number of blocks (default forever)")
@click.option('--password', default=None, help="Read the password from the command line [WARN: this method is not secure]")
def account_spend(recipient_account, amount, ttl, password):
    kp, _ = _account(password=password)
    try:
        _check_prefix(recipient_account, "ak")
        data = _epoch_cli().spend(kp, recipient_account, amount, tx_ttl=ttl)
        _print_object({
            "Transaction hash": data.tx_hash,
            "Sender account": kp.get_address(),
            "Recipient account": recipient_account,
        }, title='Transaction posted to the chain')
    except Exception as e:
        print(e)

#    _   _
#   | \ | |
#   |  \| | __ _ _ __ ___   ___  ___
#   | . ` |/ _` | '_ ` _ \ / _ \/ __|
#   | |\  | (_| | | | | | |  __/\__ \
#   |_| \_|\__,_|_| |_| |_|\___||___/
#
#


@account.group(help="Handle name lifecycle")
@click.argument('domain')
@click.pass_context
def name(ctx, domain):
    ctx.obj[CTX_AET_DOMAIN] = domain


@name.command('claim', help="Claim a domain name")
@click.option("--name-ttl", default=100, help='Lifetime of the claim in blocks (default 100)')
@click.option("--ttl", default=100, help='Lifetime of the claim request in blocks (default 100)')
@click.pass_context
def name_register(ctx, name_ttl, ttl):
    try:
        # retrieve the domain from the context
        domain = ctx.obj.get(CTX_AET_DOMAIN)
        # retrieve the keypair
        kp, _ = _account()
        name = _epoch_cli().AEName(domain)
        name.update_status()
        if name.status != AEName.Status.AVAILABLE:
            print("Domain not available")
            exit(0)
        tx = name.full_claim_blocking(kp, name_ttl=name_ttl, tx_ttl=ttl)
        _print_object(tx, title=f"Name {domain} claimed")
    except Exception as e:
        print(e)


@name.command('update')
@click.pass_context
@click.argument('address')
@click.option("--name-ttl", default=100, help='Lifetime of the claim in blocks (default 100)')
@click.option("--ttl", default=100, help='Lifetime of the claim request in blocks (default 100)')
def name_update(ctx, address, name_ttl, ttl):
    """
    Update a name pointer
    """
    # retrieve the domain from the context
    domain = ctx.obj.get(CTX_AET_DOMAIN)
    # retrieve the keypair
    kp, _ = _account()
    name = _epoch_cli().AEName(domain)
    name.update_status()
    if name.status != AEName.Status.CLAIMED:
        print(f"Domain is {name.status} and cannot be transferred")
        exit(0)
    tx = name.update(kp, target=address, name_ttl=name_ttl, tx_ttl=ttl)
    _print_object(tx, title=f"Name {domain} status {name.status}")


@name.command('revoke')
@click.pass_context
def name_revoke(ctx):
    # retrieve the domain from the context
    domain = ctx.obj.get(CTX_AET_DOMAIN)
    # retrieve the keypair
    kp, _ = _account()
    name = _epoch_cli().AEName(domain)
    name.update_status()
    if name.status == AEName.Status.AVAILABLE:
        print("Domain is available, nothing to revoke")
        exit(0)
    tx = name.revoke(kp)

    _print_object({'Transaction hash', tx.tx_hash}, title=f"Name {domain} status {name.status}")


@name.command('transfer')
@click.pass_context
@click.argument('address')
def name_transfer(ctx, address):
    """
    Transfer a name to another account
    """
    # retrieve the domain from the context
    domain = ctx.obj.get(CTX_AET_DOMAIN)
    # retrieve the keypair
    kp, _ = _account()
    name = _epoch_cli().AEName(domain)
    name.update_status()
    if name.status != AEName.Status.CLAIMED:
        print(f"Domain is {name.status} and cannot be transferred")
        exit(0)
    tx = name.transfer_ownership(kp, address)
    _print_object({'Transaction hash', tx}, title=f"Name {domain} status {name.status}")


#     ____                 _
#    / __ \               | |
#   | |  | |_ __ __ _  ___| | ___  ___
#   | |  | | '__/ _` |/ __| |/ _ \/ __|
#   | |__| | | | (_| | (__| |  __/\__ \
#    \____/|_|  \__,_|\___|_|\___||___/
#
#
@cli.group(help="Interact with oracles")
def oracle():
    pass


@oracle.command('register')
def oracle_register():
    print("register oracle")
    pass


@oracle.command('query')
def oracle_query():
    print("query oracle")
    pass


#     _____            _                  _
#    / ____|          | |                | |
#   | |     ___  _ __ | |_ _ __ __ _  ___| |_ ___
#   | |    / _ \| '_ \| __| '__/ _` |/ __| __/ __|
#   | |___| (_) | | | | |_| | | (_| | (__| |_\__ \
#    \_____\___/|_| |_|\__|_|  \__,_|\___|\__|___/
#
#
@cli.group('contract', help="Compile contracts")
def contract_off_chain():
    pass


@contract_off_chain.command(help="Compile a contract")
@click.argument("contract_file")
def contract_compile(contract_file):
    try:
        with open(contract_file) as fp:
            code = fp.read()

            contract = _epoch_cli().Contract(Contract.SOPHIA)
            result = contract.compile(code)
            _print_object({"bytecode", result})
    except Exception as e:
        print(e)


@account.group('contract', help='Deploy and execute contracts on the chain')
def contract():
    pass


@contract.command('deploy', help='Deploy a contract on the chain')
@click.argument("contract_file")
# TODO: what is gas here
@click.option("--gas", default=40000000, help='Amount of gas to deploy the contract')
def contract_deploy(contract_file, gas):
    """
    Deploy a contract to the chain and create a deploy descriptor
    with the contract informations that can be use to invoke the contract
    later on.

    The generated descriptor will be created in the same folde of the contract
    source file. Multiple deploy of the same contract file will generate different
    deploy descriptor
    """
    try:
        with open(contract_file) as fp:
            code = fp.read()
            contract = _epoch_cli().Contract(code)
            kp, _ = _account()
            tx = contract.tx_create(kp, gas=gas)

            # save the contract data
            contract_data = {
                'source': contract.source_code,
                'bytecode': contract.bytecode,
                'address': contract.address,
                'transaction': tx.tx_hash,
                'owner': kp.get_address(),
                'created_at': datetime.now().isoformat('T')
            }
            # write the contract data to a file
            deploy_descriptor = f"{contract_file}.deploy.{contract.address[3:]}.json"
            with open(deploy_descriptor, 'w') as fw:
                json.dump(contract_data, fw, indent=2)
            _print_object({
                "Contract address": contract.address,
                "Transaction hash": tx.tx_hash,
                "Deploy descriptor": deploy_descriptor,
            })
    except Exception as e:
        print(e)


@contract.command('call', help='Execute a function of the contract')
@click.pass_context
@click.argument("deploy_descriptor")
@click.argument("function")
@click.argument("params")
@click.argument("return_type")
def contract_call(ctx, deploy_descriptor, function, params, return_type):
    try:
        with open(deploy_descriptor) as fp:
            contract = json.load(fp)
            source = contract.get('source')
            bytecode = contract.get('bytecode')
            address = contract.get('address')

            kp, _ = _account()
            contract = _epoch_cli().Contract(source, bytecode=bytecode, address=address, client=_epoch_cli())
            result = contract.tx_call(kp, function, params, gas=40000000)
            _print_object({
                'Contract address': contract.address,
                'Gas price': result.gas_price,
                'Gas used': result.gas_used,
                'Return value (encoded)': result.return_value,
            })
            if result.return_type == 'ok':
                value, remote_type = contract.decode_data(result.return_value, return_type)
                _print_object({
                    'Return value': value,
                    'Return remote type': remote_type,
                })

            pass
    except Exception as e:
        print(e)


#    _____                           _
#   |_   _|                         | |
#     | |  _ __  ___ _ __   ___  ___| |_
#     | | | '_ \/ __| '_ \ / _ \/ __| __|
#    _| |_| | | \__ \ |_) |  __/ (__| |_
#   |_____|_| |_|___/ .__/ \___|\___|\__|
#                   | |
#                   |_|


@cli.command("inspect", help="Get information on transactions, blocks, etc...")
@click.argument('obj')
def inspect(obj):
    try:
        if obj.endswith(".aet"):
            name = _epoch_cli().AEName(obj)
            name.update_status()
            _print_object({
                'Status': name.status,
                'Name hash': name.name_hash,
                'Pointers': name.pointers,
                'TTL': name.name_ttl,
            })
        elif obj.startswith("kh_") or obj.startswith("mh_"):
            v = _epoch_cli().get_block_by_hash(obj)
            _print_object(v)
        elif obj.startswith("th_"):
            v = _epoch_cli().get_transaction_by_hash(hash=obj)
            _print_object(v)
        elif obj.startswith("ak_"):
            v = _epoch_cli().get_account_by_pubkey(pubkey=obj)
            _print_object(v)
        elif obj.isdigit() and obj >= 0:
            v = _epoch_cli().get_generation_by_hash(hash=obj)
            _print_object(v)
        else:
            raise ValueError(f"input not recongized: {obj}")
    except Exception as e:
        print("Error:", e)


# @inspect.command('deploy', help='The contract deploy descriptor to inspect')
# @click.argument('contract_deploy_descriptor')
# def inspect_deploy(contract_deploy_descriptor):
#     """
#     Inspect a contract deploy file that has been generated with the command
#     aecli account X contract CONTRACT_SOURCE deploy
#     """
#     try:
#         with open(contract_deploy_descriptor) as fp:
#             contract = json.load(fp)
#             _print_object(contract)
#             data = _epoch_cli().get_transaction_by_hash(hash=contract.get('transaction', 'N/A'))
#             _print_object(data, "Transaction")
#     except Exception as e:
#         print(e)


#     _____ _           _
#    / ____| |         (_)
#   | |    | |__   __ _ _ _ __
#   | |    | '_ \ / _` | | '_ \
#   | |____| | | | (_| | | | | |
#    \_____|_| |_|\__,_|_|_| |_|
#
#


@cli.group(help="Interact with the blockchain")
def chain():
    pass


@chain.command('top')
def chain_top():
    """
    Print the information of the top block of the chain.
    """
    data = _epoch_cli().get_top_block()
    _print_object(data)


@chain.command('version')
def chain_version():
    """
    Print the epoch node version.
    """
    data = _epoch_cli().get_status()
    _print_object(data)


@chain.command('play')
@click.option('--height', type=int, help="From which height should play the chain (default top)")
@click.option('--block-hash', help="From which block should play the chain (default top)")
@click.option('--limit', '-l', type=int, default=sys.maxsize, help="Limit the number of block to print")
def chain_play(height, block_hash, limit):
    """
    play the blockchain backwards
    """
    if block_hash is not None:
        _check_prefix(block_hash, "kh")
        b = _epoch_cli().get_key_block_by_hash(hash=block_hash)
    elif height is not None:
        b = _epoch_cli().get_key_block_by_height(height=height)
    else:
        b = _epoch_cli().get_top_block()
    # check the limit
    limit = limit if limit > 0 else 0
    while b is not None and limit > 0:
        try:
            _print_object(b, title=' >>>>> ')
            limit -= 1
            if limit <= 0:
                break
            b = _epoch_cli().get_key_block_by_hash(hash=b.prev_hash)
        except Exception as e:
            print(e)
            b = None
            pass


# run the client
cli(obj={})
exit(0)
