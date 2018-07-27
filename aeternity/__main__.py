import logging
import click
import os
import traceback

from aeternity import __version__

from aeternity.epoch import EpochClient
from aeternity.config import Config, MAX_TX_TTL, ConfigException
# from aeternity.oracle import Oracle, OracleQuery, NoOracleResponse
from aeternity.signing import KeyPair
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


def _epoch_cli():
    try:
        ctx = click.get_current_context()
        # set the default configuration
        Config.set_defaults(Config(
            external_url=ctx.obj.get(CTX_EPOCH_URL),
            internal_url=ctx.obj.get(CTX_EPOCH_URL_INTERNAL),
            websocket_url=ctx.obj.get(CTX_EPOCH_URL_WEBSOCKET)
        ))
    except ConfigException as e:
        print("Configuration error: ", e)
        exit(1)
    # load the epoch client
    return EpochClient()


def _keypair(password=None):
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
            password = click.prompt("Enter the wallet password", default='', hide_input=True)
        return KeyPair.read_from_private_key(kf, password), os.path.abspath(kf)
    except Exception:
        print("Invalid password")
        exit(1)


def _check_prefix(data, prefix):
    """
    helper method to check the validity of a prefix
    """

    if len(data) < 3:
        print("Invalid input, likely you forgot to escape the $ sign (use \\$)")
        exit(1)

    if not data.startswith(f"{prefix}$"):
        if prefix == 'ak':
            print("Invalid account address, it shoudld be like: ak$....")
        if prefix == 'th':
            print("Invalid transaction hash, it shoudld be like: th$....")
        if prefix == 'bh':
            print("Invalid block hash, it shoudld be like: bh$....")
        exit(1)


def _verbose():
    """tell if the command has the verbose flag"""
    ctx = click.get_current_context()
    return ctx.obj.get(CTX_VERBOSE, False)


def _print(header, value):
    print(f" {header.ljust(53, '_')} \n\n{value}\n")


def _pp(data, title=None, prefix=''):
    """
    pretty printer
    :param data: single enty or list of key-value tuples
    :param title: optional title
    :param quiet: if true print only the values
    """
    ctx = click.get_current_context()
    if title is not None:
        print(title)
    if not isinstance(data, list):
        data = [data]
    for kv in data:
        if ctx.obj.get(CTX_QUIET, False):
            print(kv[1])
        else:
            label = f"{prefix}{kv[0]}"
            print(f"{label.ljust(30, '_')} {kv[1]}")


def _ppe(error):
    """pretty printer for errors"""
    ctx = click.get_current_context()
    print(error)
    if ctx.obj.get(CTX_VERBOSE, True):
        traceback.print_exc()


def _p_block(block):
    """Print info of a block """
    block_info = [
        ('Block hash', block.hash),
        ('Block height', block.height),
        ('State hash', block.state_hash),
        ('Miner', block.miner if hasattr(block, 'miner') else 'n/a'),
        ('Time', datetime.fromtimestamp(block.time / 1000, timezone.utc).isoformat('T')),
        ('Previous block hash', block.prev_hash),
        ('Transactions', len(block.transactions) if hasattr(block, 'transactions') else 0)
    ]
    _pp(block_info)
    if hasattr(block, 'transactions'):
        for tx in block.transactions:
            _pp(('Tx Hash', tx.get('hash')), prefix='>  ')
            _pp(('Signatures', tx.get('signatures')), prefix='   ')
            _pp(('Sender', tx.get('tx', {}).get('sender')), prefix='   ')
            _pp(('Recipient', tx.get('tx', {}).get('recipient')), prefix='   ')
            _pp(('Amount', tx.get('tx', {}).get('amount')), prefix='   ')


def _p_tx(tx):
    """Print info of a transactions"""
    _pp([
        ('Block hash', tx.get('block_hash')),
        ('Block height', tx.get('block_height')),
        ('Signatures', tx.get('signatures')),
        ('Sender account', tx.get('tx', {}).get('sender')),
        ('Recipient account', tx.get('tx', {}).get('recipient')),
        ('Amount', tx.get('tx', {}).get('amount')),
        ('TTL', tx.get('tx', {}).get('ttl'))
    ])


# Commands
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# the priority for the url selection is PARAM, ENV, DEFAULT


@click.group()
@click.pass_context
@click.version_option()
@click.option('--url', '-u', default='https://sdk-testnet.aepps.com', envvar='EPOCH_URL', help='Epoch node url', metavar='URL')
@click.option('--url-internal', '-i', default='https://sdk-testnet.aepps.com/internal', envvar='EPOCH_URL_INTERNAL', metavar='URL')
@click.option('--url-websocket', '-w', default='ws://sdk-testnet.aepps.com', envvar='EPOCH_URL_WEBSOCKET', metavar='URL')
@click.option('--quiet', '-q', default=False, is_flag=True, help='Print only results')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Print verbose data')
@click.version_option(version=__version__)
def cli(ctx, url, url_internal, url_websocket, quiet, verbose):
    """
    Welcome to the aecli client.

    The client is to interact with an epoch node.

    """
    ctx.obj[CTX_EPOCH_URL] = url
    ctx.obj[CTX_EPOCH_URL_INTERNAL] = url_internal
    ctx.obj[CTX_EPOCH_URL_WEBSOCKET] = url_websocket
    ctx.obj[CTX_QUIET] = quiet
    ctx.obj[CTX_VERBOSE] = verbose

#   __          __   _ _      _
#   \ \        / /  | | |    | |
#    \ \  /\  / /_ _| | | ___| |_ ___
#     \ \/  \/ / _` | | |/ _ \ __/ __|
#      \  /\  / (_| | | |  __/ |_\__ \
#       \/  \/ \__,_|_|_|\___|\__|___/
#
#


@cli.group(help="Handle wallet operations")
@click.pass_context
@click.argument('key_path', default='sign_key', envvar='WALLET_SIGN_KEY_PATH')
def wallet(ctx, key_path):
    ctx.obj[CTX_KEY_PATH] = key_path


@wallet.command('create', help="Create a new wallet")
@click.pass_context
@click.option('--password', default=None, help="Set a password from the command line [WARN: this method is not secure]")
@click.option('--force', default=False, is_flag=True, help="Overwrite exising keys without asking")
def wallet_create(ctx, password, force):
    kp = KeyPair.generate()
    kf = ctx.obj.get(CTX_KEY_PATH)
    if not force and os.path.exists(kf):
        click.confirm(f'Key file {kf} already exists, overwrite?', abort=True)
    if password is None:
        password = click.prompt("Enter the wallet password", default='', hide_input=True)
    kp.save_to_file(kf, password)
    _pp([
        ('Wallet address', kp.get_address()),
        ('Wallet path', os.path.abspath(kf))
    ], title='Wallet created')


@wallet.command('save', help='Save a private keys string to a password protected file wallet')
@click.argument("private_key")
@click.pass_context
def wallet_save(ctx, private_key):
    try:
        kp = KeyPair.from_private_key_string(private_key)
        kf = ctx.obj.get(CTX_KEY_PATH)
        if os.path.exists(kf):
            click.confirm(f'Key file {kf} already exists, overwrite?', abort=True)
        password = click.prompt("Enter the wallet password", default='', hide_input=True)
        kp.save_to_file(kf, password)
        _pp([
            ('Wallet address', kp.get_address()),
            ('Wallet path', os.path.abspath(kf))
        ], title='Wallet saved')
    except Exception as e:
        _ppe(e)


@wallet.command('address', help="Print the wallet address (public key)")
@click.option('--password', default=None, help="Read the password from the command line [WARN: this method is not secure]")
def wallet_address(password):
    kp, kf = _keypair(password=password)
    _pp([
        ('Wallet address', kp.get_address()),
    ])


@wallet.command('balance', help="Get the balance of a wallet")
@click.option('--password', default=None, help="Read the password from the command line [WARN: this method is not secure]")
def wallet_balance(password):
    kp, _ = _keypair(password=password)

    try:
        balance = _epoch_cli().get_balance(kp.get_address())
        _pp(
            ("Account balance", balance)
        )
    except Exception as e:
        _ppe(e)


@wallet.command('spend', help="Create a transaction to another wallet")
@click.argument('recipient_account', required=True)
@click.argument('amount', required=True, default=1)
@click.option('--ttl', default=MAX_TX_TTL, help="Validity of the spend transaction in number of blocks (default forever)")
@click.option('--password', default=None, help="Read the password from the command line [WARN: this method is not secure]")
def wallet_spend(recipient_account, amount, ttl, password):
    kp, _ = _keypair(password=password)
    try:
        _check_prefix(recipient_account, "ak")
        data = _epoch_cli().spend(kp, recipient_account, amount, tx_ttl=ttl)
        _pp([
            ("Transaction hash", data[1]),
            ("Sender account", kp.get_address()),
            ("Recipient account", recipient_account),
        ], title='Transaction posted to the chain')
    except Exception as e:
        _ppe(e)

#    _   _
#   | \ | |
#   |  \| | __ _ _ __ ___   ___  ___
#   | . ` |/ _` | '_ ` _ \ / _ \/ __|
#   | |\  | (_| | | | | | |  __/\__ \
#   |_| \_|\__,_|_| |_| |_|\___||___/
#
#


@wallet.group(help="Handle name lifecycle")
@click.argument('domain')
@click.pass_context
def name(ctx, domain):
    ctx.obj[CTX_AET_DOMAIN] = domain


@name.command('claim', help="Claim a domain name")
@click.option("--name-ttl", default=100, help='Lifetime of the claim in blocks')
@click.pass_context
def name_register(ctx, name_ttl):
    # retrieve the domain from the context
    domain = ctx.obj.get(CTX_AET_DOMAIN)
    # retrieve the keypair
    kp, _ = _keypair()
    name = AEName(domain)
    name.update_status()
    if name.status != AEName.Status.AVAILABLE:
        print("Domain not available")
        exit(0)
    name.full_claim_blocking(kp, name_ttl=name_ttl)
    print(f"Name {domain} claimed")
    pass


@name.command('update')
def name_update():
    print("update name")
    pass


@name.command('revoke')
def name_revoke():
    print("revoke name")
    pass


@name.command('transfer')
def name_transfer():
    print("transfer name")
    pass


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
@cli.group("Compile, deploy and execute contracts")
def contract():
    pass


@contract.command('compile', help="Compile a contract")
@click.argument("contract_file")
def contract_compile(contract_file):
    try:
        with open(contract_file) as fp:
            c = fp.read()
            print(c)
            contract = Contract(fp.read(), Contract.SOPHIA, client=_epoch_cli())
            result = contract.compile('')
            _pp([
                ("contract", result)
            ])
    except Exception as e:
        print(e)


@contract.command('deploy', help='Deploy a contract on the chain')
@click.argument("contract_file")
# TODO: what is gas here
@click.option("--gas", default=1000, help='Amount of gas to deploy the contract')
def contract_deploy(contract_file, gas):
    try:
        with open(contract_file) as fp:
            contract = Contract(fp.read(), Contract.SOPHIA, client=_epoch_cli())
            kp, _ = _keypair()
            address, tx = contract.tx_create(kp, gas=gas)
            _pp([
                ("Contract address", address),
                ("Transaction hash", tx.tx_hash),
            ])
    except Exception as e:
        print(e)


@contract.command('call', help='Execute a function of the contract')
@click.pass_context
@click.argument('key_path', default='sign_key', envvar='WALLET_SIGN_KEY_PATH')
@click.argument("contract_address")
@click.argument("function")
@click.argument("params")
def contract_call(ctx, key_path, contract_address, function, params):
    try:
        ctx.obj[CTX_KEY_PATH] = key_path
        kp = _keypair()
        result = contract.tx_call(contract_address, kp, function, params)
        if result.return_type == 'ok':
            print(result)
        print("call contract")
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


@cli.group(help="Get information on transactions, blocks, etc...")
def inspect():
    pass


@inspect.command('block', help='The block hash to inspect (eg: bh$...)')
@click.argument('block_hash')
def inspect_block(block_hash):
    _check_prefix(block_hash, "bh")
    data = _epoch_cli().get_block_by_hash(block_hash)
    _p_block(data)


@inspect.command('height', help='The height of the chain to inspect (eg:14352)')
@click.argument('chain_height', default=1)
def inspect_height(chain_height):
    data = _epoch_cli().get_key_block_by_height(chain_height)
    _p_block(data)


@inspect.command('transaction', help='The transaction hash to inspect (eg: th$...)')
@click.argument('tx_hash')
def inspect_transaction(tx_hash):
    _check_prefix(tx_hash, "th")
    data = _epoch_cli().get_transaction_by_transaction_hash(tx_hash)
    _p_tx(data.transaction)


@inspect.command('account', help='The address of the account to inspect (eg: ak$...)')
@click.argument('account')
def inspect_account(account):
    _check_prefix(account, "ak")
    try:
        data = _epoch_cli().get_balance(account)
        _pp(("Account balance", data))
    except Exception as e:
        print(e)


@inspect.command('name', help='The name to inspect (eg: mydomain.aet)')
@click.argument('domain')
def inspect_name(domain):
    try:
        name = AEName(domain, client=_epoch_cli())
        name.update_status()
        info = [('Status', name.status)]
        if len(name.pointers) > 0:
            info.append(('Pointers', name.pointers))
            info.append(('TTL', name.name_ttl))
        _pp(info)
    except Exception as e:
        print(e)


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
    data = _epoch_cli().get_top()
    _p_block(data)


@chain.command('version')
def chain_version():
    """
    Print the epoch node version.
    """
    data = _epoch_cli().get_version()
    _pp(("Epoch node version", data))


# run the client
cli(obj={})
exit(0)
