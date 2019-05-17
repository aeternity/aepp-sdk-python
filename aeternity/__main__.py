import logging
import click
import os
import json
import sys
import getpass
import namedtupled

from aeternity import _version

from aeternity.node import NodeClient, Config
from aeternity.transactions import TxSigner, TxBuilder
from aeternity.identifiers import NETWORK_ID_MAINNET
from . import utils, signing, aens, defaults, exceptions
from aeternity.contract import CompilerClient

from datetime import datetime, timezone


logging.basicConfig(format='%(message)s', level=logging.INFO)


CTX_NODE_URL = 'NODE_URL'
CTX_NODE_URL_DEBUG = 'NODE_URL_DEBUG'
CTX_NODE_WS = 'NODE_URL_WS'
CTX_KEY_PATH = 'KEY_PATH'
CTX_QUIET = 'QUIET'
CTX_AET_DOMAIN = 'AET_NAME'
CTX_FORCE_COMPATIBILITY = 'CTX_FORCE_COMPATIBILITY'
CTX_BLOCKING_MODE = 'CTX_BLOCKING_MODE'
CTX_OUTPUT_JSON = 'CTX_OUTPUT_JSON'


def _node_cli(network_id=None):
    try:
        ctx = click.get_current_context()
        # set the default configuration
        cfg = Config(
            external_url=ctx.obj.get(CTX_NODE_URL),
            internal_url=ctx.obj.get(CTX_NODE_URL_DEBUG),
            websocket_url=ctx.obj.get(CTX_NODE_WS),
            force_compatibility=ctx.obj.get(CTX_FORCE_COMPATIBILITY),
            blocking_mode=ctx.obj.get(CTX_BLOCKING_MODE),
            network_id=network_id
        )
        # load the aeternity node client
        return NodeClient(cfg)

    except exceptions.ConfigException as e:
        _print_error(e, title="configuration error", exit_code=1)
    except exceptions.UnsupportedNodeVersion as e:
        _print_error(e, exit_code=1)


def _account(keystore_name, password=None):
    """
    utility function to get the keypair from the click context
    :return: (account, keypath)
    """
    ctx = click.get_current_context()
    kf = ctx.obj.get(CTX_KEY_PATH) if keystore_name is None else keystore_name
    if not os.path.exists(kf):
        print(f'Key file {kf} does not exits.')
        exit(1)
    try:
        if password is None:
            password = getpass.getpass("Enter the account password: ")
        return signing.Account.from_keystore(kf, password), os.path.abspath(kf)
    except Exception as e:
        _print_error(e, title="keystore decryption failed", exit_code=1)


def _pl(label, offset, value=None):
    if label is None:
        return
    if value is None:
        lo = " " * offset
        print(f"{lo}{label.capitalize().replace('_',' ')}")
        return
    else:
        lo = " " * offset
        lj = 53 - len(lo)
        if len(label) > 0:
            lv = label.capitalize().replace('_', ' ')
            lv = f"{lv} ".ljust(lj, '_')
        else:
            lv = ' ' * lj
        print(f"{lo}{lv} {value}")


def _po(label, value, offset=0, label_prefix=None):
    """
    pretty printer
    :param data: single entry or list of key-value tuples
    :param title: optional title
    :param quiet: if true print only the values
    """
    label = label if label_prefix is None else f"{label_prefix} {label}"
    if isinstance(value, dict):
        _pl(f"<{label}>", offset)
        o = offset + 2
        for k, v in value.items():
            _po(k, v, o)
        _pl(f"</{label}>", offset)
    elif isinstance(value, tuple):
        _pl(f"<{label}>", offset)
        o = offset + 2
        for k, v in value._asdict().items():
            _po(k, v, o)
        _pl(f"</{label}>", offset)
    elif isinstance(value, list):
        if label == "pow":
            return
        _pl(f"<{label} {len(value)}>", offset)
        o = offset + 2
        for i, x in enumerate(value):
            _po(f"{label[:-1]} #{i+1}", x, o)
        _pl(f"</{label}>", offset)
    elif isinstance(value, datetime):
        val = value.strftime("%Y-%m-%d %H:%M")
        _pl(label, offset, value=val)
    else:
        if label.lower() == "time":
            value = datetime.fromtimestamp(value / 1000, timezone.utc).isoformat('T')
        elif label.lower() in ["amount", "balance", "channel_amount",
                               "channel_reserve", "deposit", "fee", "gas_price",
                               "gas", "initiator_amount_final", "initiator_amount",
                               "push_amount", "query_fee", "responder_amount_final",
                               "responder_amount", "round", "solo_round"]:
            value = utils.format_amount(value)

        _pl(label, offset, value=value)


def _print_object(data, title):
    ctx = click.get_current_context()

    if ctx.obj.get(CTX_OUTPUT_JSON, False):
        if isinstance(data, tuple):
            print(json.dumps(namedtupled.reduce(data), indent=2))
            return
        if isinstance(data, str):
            print(data)
            return
        print(json.dumps(data, indent=2))
        return

    _po(title, data)


def _print_error(err, title="error", exit_code=0):
    _print_object({"message": str(err)}, title)
    sys.exit(exit_code)


# Commands
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# set global options TODO: this is a bit silly, we should probably switch back to stdlib
_global_options = [
    click.option('--json', 'json_', is_flag=True, default=False, help='Print output in JSON format'),
]

_online_options = [
    click.option('--force', is_flag=True, default=False, help='Ignore aeternity node version compatibility check'),
    click.option('--wait', is_flag=True, default=False, help='Wait for transactions to be included'),
]

_account_options = [
    click.option('--password', default=None, help="Read account password from stdin [WARN: this method is not secure]")
]

_sign_options = [
    click.option('--network-id', default=NETWORK_ID_MAINNET, help="The network id to use when signing a transaction", show_default=True)
]

_transaction_options = [
    click.option('--ttl', 'ttl', type=int, default=defaults.TX_TTL,
                 help=f'Set the transaction ttl (relative number, ex 100)', show_default=True),
    click.option('--fee', 'fee', type=int, default=defaults.FEE,
                 help=f'Set the transaction fee', show_default=True),
    click.option('--nonce', 'nonce', type=int, default=0, help='Set the transaction nonce, if not set it will automatically generated'),
]


def global_options(func):
    for option in reversed(_global_options):
        func = option(func)
    return func


def online_options(func):
    for option in reversed(_online_options):
        func = option(func)
    return func


def account_options(func):
    for option in reversed(_account_options):
        func = option(func)
    return func


def sign_options(func):
    for option in reversed(_sign_options):
        func = option(func)
    return func


def transaction_options(func):
    for option in reversed(_transaction_options):
        func = option(func)
    return func


def set_global_options(json_, force=False, wait=False):
    ctx = click.get_current_context()
    ctx.obj[CTX_FORCE_COMPATIBILITY] = force
    ctx.obj[CTX_BLOCKING_MODE] = wait
    ctx.obj[CTX_OUTPUT_JSON] = json_

# the priority for the url selection is PARAM, ENV, DEFAULT


@click.group()
@click.pass_context
@click.version_option()
@click.option('--url', '-u', default='https://sdk-mainnet.aepps.com', envvar='NODE_URL', help='Aeternity node url', metavar='URL')
@click.option('--debug-url', '-d', default=None, envvar='NODE_URL_DEBUG', metavar='URL')
@global_options
@click.version_option(version=_version())
def cli(ctx, url, debug_url, json_):
    """
    Welcome to the aecli client.

    The client is to interact with an aeternity node.

    """
    ctx.obj[CTX_NODE_URL] = url
    ctx.obj[CTX_NODE_URL_DEBUG] = debug_url


@cli.command('config', help="Print the client configuration")
@click.pass_context
def config_cmd(ctx):
    _print_object({
        "Node URL": ctx.obj.get(CTX_NODE_URL),
    }, title="aecli settings")


#        _                                               _
#       / \                                             / |_
#      / _ \     .---.  .---.   .--.   __   _   _ .--. `| |-'.--.
#     / ___ \   / /'`\]/ /'`\]/ .'`\ \[  | | | [ `.-. | | | ( (`\]
#   _/ /   \ \_ | \__. | \__. | \__. | | \_/ |, | | | | | |, `'.'.
#  |____| |____|'.___.''.___.' '.__.'  '.__.'_/[___||__]\__/[\__) )
#


@cli.group(help="Handle account operations")
def account():
    pass


@account.command('create', help="Create a new account")
@click.argument('keystore_name')
@click.option('--overwrite', default=False, is_flag=True, help="Overwrite existing keys without asking", show_default=True)
@global_options
@account_options
def account_create(keystore_name, password, overwrite, json_):
    try:
        set_global_options(json_)
        new_account = signing.Account.generate()
        # TODO: introduce default configuration path
        if not overwrite and os.path.exists(keystore_name):
            click.confirm(f'Keystore file {keystore_name} already exists, overwrite?', abort=True)
        if password is None:
            password = click.prompt("Enter the account password", default='', hide_input=True)
        new_account.save_to_keystore_file(keystore_name, password)
        _print_object({
            'Address': new_account.get_address(),
            'Path': os.path.abspath(keystore_name)
        }, title='account')
    except Exception as e:
        _print_error(e, exit_code=1)


@account.command('save', help='Save a private keys string to a password protected file account')
@click.argument('keystore_name', required=True)
@click.argument('private_key', required=True)
@click.option('--overwrite', default=False, is_flag=True, help="Overwrite existing keys without asking", show_default=True)
@global_options
@account_options
def account_save(keystore_name, private_key, password, overwrite, json_):
    try:
        set_global_options(json_)
        account = signing.Account.from_private_key_string(private_key)
        if not overwrite and os.path.exists(keystore_name):
            click.confirm(f'Keystore file {keystore_name} already exists, overwrite?', abort=True)
        if password is None:
            password = click.prompt("Enter the account password", default='', hide_input=True)
        account.save_to_keystore_file(keystore_name, password)
        _print_object({
            'Address': account.get_address(),
            'Path': os.path.abspath(keystore_name)
        }, title='account')
    except Exception as e:
        _print_error(e, exit_code=1)


@account.command('address', help="Print the account address (public key)")
@click.argument('keystore_name')
@click.option('--private-key', is_flag=True, help="Print the private key instead of the account address")
@global_options
@account_options
def account_address(password, keystore_name, private_key, json_):
    try:
        set_global_options(json_)
        account, keystore_path = _account(keystore_name, password=password)
        o = {'Address': account.get_address()}
        if private_key:
            click.confirm(f'!Warning! this will print your private key on the screen, are you sure?', abort=True)
            o["Signing key"] = account.get_private_key()
        _print_object(o, title='account')
    except Exception as e:
        _print_error(e, exit_code=1)


@account.command('balance', help="Get the balance of a account")
@click.argument('keystore_name')
@global_options
@account_options
@online_options
@click.option('--height', type=int, default=None, help="Retrieve the balance at the provided height")
def account_balance(keystore_name, password, height, force, wait, json_):
    try:
        set_global_options(json_, force, wait)
        account, _ = _account(keystore_name, password=password)
        if height is not None and height > 0:
            account = _node_cli().get_account_by_pubkey_and_height(pubkey=account.get_address(), height=height)
            _print_object(account, title=f"account at {height}")
            return
        account = _node_cli().get_account_by_pubkey(pubkey=account.get_address())
        _print_object(account, title="account")
    except Exception as e:
        _print_error(e, exit_code=1)


@account.command('spend', help="Create a transaction to another account")
@click.argument('keystore_name', required=True)
@click.argument('recipient_id', required=True)
@click.argument('amount', required=True, type=int)
@click.option('--payload', default="", help="Spend transaction payload")
@global_options
@account_options
@online_options
@transaction_options
@sign_options
def account_spend(keystore_name, recipient_id, amount, payload, fee, ttl, nonce, password, network_id, force, wait, json_):
    try:
        set_global_options(json_, force, wait)
        account, keystore_path = _account(keystore_name, password=password)
        account.nonce = nonce
        if not utils.is_valid_hash(recipient_id, prefix="ak"):
            raise ValueError("Invalid recipient address")
        tx = _node_cli(network_id=network_id).spend(account, recipient_id, amount, tx_ttl=ttl, fee=fee, payload=payload)
        _print_object(tx, title='spend transaction')
    except Exception as e:
        _print_error(e, exit_code=1)


@account.command('transfer', help="Create a transaction to transfer a percentage of funds to another account")
@click.argument('keystore_name', required=True)
@click.argument('recipient_id', required=True)
@click.argument('transfer_amount', required=True, type=float)
@click.option('--payload', default="", help="Spend transaction payload")
@click.option('--include-fee', is_flag=True, default=True, help="Whatever to include the fee in the amount transferred")
@global_options
@account_options
@online_options
@transaction_options
@sign_options
def account_transfer_amount(keystore_name, recipient_id, transfer_amount, include_fee, payload, fee, ttl, nonce, password, network_id, force, wait, json_):
    try:
        set_global_options(json_, force, wait)
        account, keystore_path = _account(keystore_name, password=password)
        account.nonce = nonce
        if not utils.is_valid_hash(recipient_id, prefix="ak"):
            raise ValueError("Invalid recipient address")
        tx = _node_cli(network_id=network_id).transfer_funds(account, recipient_id, transfer_amount, tx_ttl=ttl, payload=payload, include_fee=include_fee)
        _print_object(tx, title='spend transaction')
    except Exception as e:
        _print_error(e, exit_code=1)


@account.command('sign', help="Sign a transaction")
@click.argument('keystore_name', required=True)
@click.argument('unsigned_transaction', required=True)
@global_options
@account_options
@sign_options
def account_sign(keystore_name, password, network_id, unsigned_transaction, json_):
    try:
        set_global_options(json_)
        account, keystore_path = _account(keystore_name, password=password)
        if not utils.is_valid_hash(unsigned_transaction, prefix="tx"):
            raise ValueError("Invalid transaction format")
        # force offline mode for the node_client
        tx = TxSigner(account, network_id).sign_encode_transaction(unsigned_transaction)
        _print_object(tx, title='signed transaction')
    except Exception as e:
        _print_error(e, exit_code=1)

#   _________  ____  ____
#  |  _   _  ||_  _||_  _|
#  |_/ | | \_|  \ \  / /
#      | |       > `' <
#     _| |_    _/ /'`\ \_
#    |_____|  |____||____|
#


@cli.group(help="Handle transactions creation")
def tx():
    """
    The tx command allow you to create unsigned transactions that can be broadcast
    later after being signed.
    """
    pass


@tx.command('broadcast', help='Broadcast a transaction to the network')
@click.argument('signed_transaction', required=True)
@global_options
@online_options
def tx_broadcast(signed_transaction, force, wait, json_):
    try:
        set_global_options(json_, force, wait)
        if not utils.is_valid_hash(signed_transaction, prefix="tx"):
            raise ValueError("Invalid transaction format")
        cli = _node_cli()
        tx_hash = cli.broadcast_transaction(signed_transaction)
        _print_object({
            "Transaction hash": tx_hash,
        }, title='transaction broadcast')
    except Exception as e:
        _print_error(e, exit_code=1)


@tx.command('spend', help="Create a transaction to another account")
@click.argument('sender_id', required=True)
@click.argument('recipient_id', required=True)
@click.argument('amount', required=True, type=int)
@click.option('--payload', default="", help="Spend transaction payload")
@global_options
@transaction_options
def tx_spend(sender_id, recipient_id, amount,  ttl, fee, nonce, payload, json_):
    try:
        set_global_options(json_)
        tx = TxBuilder().tx_spend(sender_id, recipient_id, amount, payload, fee, ttl, nonce)
        # print the results
        _print_object(tx, title='spend tx')
    except Exception as e:
        _print_error(e, exit_code=1)

#    _   _
#   | \ | |
#   |  \| | __ _ _ __ ___   ___  ___
#   | . ` |/ _` | '_ ` _ \ / _ \/ __|
#   | |\  | (_| | | | | | |  __/\__ \
#   |_| \_|\__,_|_| |_| |_|\___||___/
#
#


@cli.group(help="Handle name lifecycle")
def name():
    pass


@name.command('pre-claim', help="Pre-claim a domain name")
@click.argument('keystore_name', required=True)
@click.argument('domain', required=True)
@global_options
@account_options
@online_options
@transaction_options
@sign_options
def name_pre_claim(keystore_name, domain, ttl, fee, nonce, password, network_id, force, wait, json_):
    try:
        set_global_options(json_, force, wait)
        account, _ = _account(keystore_name, password=password)
        name = _node_cli(network_id=network_id).AEName(domain)
        name.update_status()
        if name.status != aens.AEName.Status.AVAILABLE:
            print("Domain not available")
            exit(0)
        # preclaim
        tx = name.preclaim(account, fee, ttl)
        _print_object(tx, title='preclaim transaction')
    except ValueError as e:
        _print_error(e, exit_code=1)
    except Exception as e:
        _print_error(e, exit_code=1)


@name.command('claim', help="Claim a domain name")
@click.argument('keystore_name', required=True)
@click.argument('domain', required=True)
@click.option("--name-ttl", default=defaults.NAME_TTL, help=f'Lifetime of the name in blocks', show_default=True, type=int)
@click.option("--name-salt", help=f'Salt used for the pre-claim transaction', required=True, type=int)
@click.option("--preclaim-tx-hash", help=f'The transaction hash of the pre-claim', required=True)
@global_options
@account_options
@online_options
@transaction_options
@sign_options
def name_claim(keystore_name, domain, name_ttl, name_salt, preclaim_tx_hash, ttl, fee, nonce, password, network_id, force, wait, json_):
    try:
        set_global_options(json_, force, wait)
        account, _ = _account(keystore_name, password=password)
        name = _node_cli(network_id=network_id).AEName(domain)
        name.update_status()
        if name.status != aens.AEName.Status.AVAILABLE:
            print("Domain not available")
            exit(0)
        # claim
        tx = name.claim(account, name_salt, preclaim_tx_hash, fee=fee, tx_ttl=ttl)
        _print_object(tx, title=f'Name {domain} claim transaction')
    except ValueError as e:
        _print_error(e, exit_code=1)
    except Exception as e:
        _print_error(e, exit_code=1)


@name.command('update')
@click.argument('keystore_name', required=True)
@click.argument('domain', required=True)
@click.argument('address', required=True)
@click.option("--name-ttl", default=defaults.NAME_TTL, help=f'Lifetime of the claim in blocks', show_default=True)
@global_options
@account_options
@online_options
@transaction_options
@sign_options
def name_update(keystore_name, domain, address, name_ttl, ttl, fee, nonce, password, network_id, force, wait, json_):
    """
    Update a name pointer
    """
    try:
        set_global_options(json_, force, wait)
        account, _ = _account(keystore_name, password=password)
        name = _node_cli(network_id=network_id).AEName(domain)
        name.update_status()
        if name.status != name.Status.CLAIMED:
            print(f"Domain is {name.status} and cannot be transferred")
            exit(0)
        tx = name.update(account, target=address, name_ttl=name_ttl, tx_ttl=ttl)
        _print_object(tx, title=f"Name {domain} status update")
    except Exception as e:
        _print_error(e, exit_code=1)


@name.command('revoke', help="Revoke a claimed name")
@click.argument('keystore_name', required=True)
@click.argument('domain', required=True)
@global_options
@account_options
@online_options
@transaction_options
@sign_options
def name_revoke(keystore_name, domain, ttl, fee, nonce, password, network_id, force, wait, json_):
    try:
        set_global_options(json_, force, wait)
        account, _ = _account(keystore_name, password=password)
        name = _node_cli(network_id=network_id).AEName(domain)
        name.update_status()
        if name.status == name.Status.AVAILABLE:
            print("Domain is available, nothing to revoke")
            exit(0)
        tx = name.revoke(account)
        _print_object(tx, title=f"Name {domain} status revoke")
    except Exception as e:
        _print_error(e, exit_code=1)


@name.command('transfer', help="Transfer a claimed domain to another account")
@click.argument('keystore_name', required=True)
@click.argument('domain', required=True)
@click.argument('address')
@global_options
@account_options
@online_options
@transaction_options
@sign_options
def name_transfer(keystore_name, domain, address, ttl, fee, nonce, password, network_id, force, wait, json_):
    """
    Transfer a name to another account
    """
    try:
        set_global_options(json_, force, wait)
        account, _ = _account(keystore_name, password=password)
        name = _node_cli(network_id=network_id).AEName(domain)
        name.update_status()
        if name.status != name.Status.CLAIMED:
            print(f"Domain is {name.status} and cannot be transferred")
            exit(0)
        tx = name.transfer_ownership(account, address)
        _print_object(tx, title=f"Name {domain} status transfer to {address}")
    except Exception as e:
        _print_error(e, exit_code=1)


#     _____            _                  _
#    / ____|          | |                | |
#   | |     ___  _ __ | |_ _ __ __ _  ___| |_ ___
#   | |    / _ \| '_ \| __| '__/ _` |/ __| __/ __|
#   | |___| (_) | | | | |_| | | (_| | (__| |_\__ \
#    \_____\___/|_| |_|\__|_|  \__,_|\___|\__|___/
#
#

@cli.group(help="Interact with Æternity smart contract compiler")
def compiler():
    pass


@compiler.command('compile', help="Compile a contract")
@click.option('--compiler-url', '-c', default='http://localhost:3080', envvar='COMPILER_URL', help='Aeternity compiler url', metavar='URL')
@click.argument("contract_file")
@global_options
def contract_compile(contract_file, compiler_url, json_):
    try:
        set_global_options(json_, False, False)
        with open(contract_file) as fp:
            code = fp.read()
            c = CompilerClient(compiler_url)
            result = c.compile(code)
            if click.confirm(f'Save contract bytecode to file ({contract_file}.bin) ?', default=True, show_default=True):
                with open(f"{contract_file}.bin", "w") as fp:
                    fp.write(result.bytecode)
            _print_object(result, title="contract")
    except Exception as e:
        _print_error(e, exit_code=1)


@compiler.command('aci', help="Get the aci of a contract")
@click.option('--compiler-url', '-c', default='http://localhost:3080', envvar='COMPILER_URL', help='Aeternity compiler url', metavar='URL')
@click.argument("contract_file")
@global_options
def contract_aci(contract_file, compiler_url, json_):
    try:
        set_global_options(json_, False, False)
        with open(contract_file) as fp:
            code = fp.read()
            c = CompilerClient(compiler_url)
            result = c.aci(code)
            _print_object(result, title="contract")
    except Exception as e:
        _print_error(e, exit_code=1)


@compiler.command('encode-calldata', help="Encode the calldata to invoke a contract")
@click.option('--compiler-url', '-c', default='http://localhost:3080', envvar='COMPILER_URL', help='Aeternity compiler url', metavar='URL')
@click.argument("contract_file")
@click.argument("function_name")
@click.option("--arguments", default=None, help="Argument of the function if any, comma separated")
@global_options
def contract_encode_calldata(contract_file, function_name, arguments, compiler_url, json_):
    try:
        set_global_options(json_, False, False)
        with open(contract_file) as fp:
            code = fp.read()
            c = CompilerClient(compiler_url)
            arguments = [] if arguments is None else arguments.split(",")
            result = c.encode_calldata(code, function_name, arguments=arguments)
            _print_object(result, title="contract")
    # except Exception as e:
    #     _print_error(e, exit_code=1)
    finally:
        pass


@compiler.command('decode-data', help="Decode the data retrieve from a contract")
@click.option('--compiler-url', '-c', default='http://localhost:3080', envvar='COMPILER_URL', help='Aeternity compiler url', metavar='URL')
@click.argument("sophia_type")
@click.argument("encoded_data")
@global_options
def contract_decode_data(contract_file, encoded_data, sophia_type, compiler_url, json_):
    try:
        set_global_options(json_, False, False)
        c = CompilerClient(compiler_url)
        result = c.decode_data(sophia_type, encoded_data)
        _print_object(result, title="contract")
    except Exception as e:
        _print_error(e, exit_code=1)


@cli.group(help='Deploy and execute contracts on the chain')
def contracts():
    pass


@contracts.command('deploy', help='Deploy a contract on the chain')
@click.argument('keystore_name', required=True)
@click.argument("bytecode_file", required=True)
@click.option("--init-calldata", default=defaults.CONTRACT_INIT_CALLDATA, help="The calldata for the init function", show_default=True)
@click.option("--gas", default=defaults.CONTRACT_GAS, help='Amount of gas to deploy the contract', show_default=True)
@click.option("--amount", default=defaults.CONTRACT_AMOUNT, help='Amount of tokens to transfer to the contract', show_default=True)
@click.option("--gas-price", default=defaults.CONTRACT_GAS_PRICE, help='The gas price used to execute the contract init function', show_default=True)
@click.option("--deposit", default=defaults.CONTRACT_AMOUNT, help='A initial deposit to the contract', show_default=True)
@global_options
@account_options
@online_options
@transaction_options
@sign_options
def contract_deploy(keystore_name, bytecode_file, init_calldata, gas, gas_price, amount, deposit, password, ttl, fee, nonce, network_id, force, wait, json_):
    """
    Deploy a contract to the chain and create a deploy descriptor
    with the contract informations that can be use to invoke the contract
    later on.

    The generated descriptor will be created in the same folde of the contract
    source file. Multiple deploy of the same contract file will generate different
    deploy descriptor
    """
    print("Not yet implemented")
    return
    try:
        with open(bytecode_file) as fp:
            set_global_options(json_, force, wait)
            account, _ = _account(keystore_name, password=password)
            bytecode = fp.read()
            contract = _node_cli(network_id=network_id).Contract()
            tx = contract.create(account, bytecode, init_calldata=init_calldata, gas=gas, amount=amount,
                                 gas_price=gas_price, deposit=deposit, tx_ttl=ttl, fee=fee)
            _print_object(tx, title="contract create")
    except Exception as e:
        _print_error(e, exit_code=1)


@contracts.command('call', help='Execute a function of the contract')
@click.argument('keystore_name', required=True)
@click.argument("deploy_descriptor", required=True)
@click.argument("function", required=True)
@click.argument("params", required=True)
@click.argument("return_type", required=True)
@click.option("--gas", default=defaults.CONTRACT_GAS, help='Amount of gas to deploy the contract', show_default=True)
@global_options
@account_options
@online_options
@transaction_options
@sign_options
def contract_call(keystore_name, deploy_descriptor, function, params, return_type, gas,  password, network_id, force, wait, json_):
    print("Not yet implemented")
    return
    try:
        with open(deploy_descriptor) as fp:
            contract = json.load(fp)
            source = contract.get('source')
            bytecode = contract.get('bytecode')
            address = contract.get('address')

            set_global_options(json_, force, wait)
            account, _ = _account(keystore_name, password=password)

            contract = _node_cli(network_id=network_id).Contract(source, bytecode=bytecode, address=address)
            tx = contract.tx_call(account, function, params, gas=gas)
            _print_object(tx, "contract call")
    except Exception as e:
        _print_error(e, exit_code=1)


@contracts.command('call-info', help='Retrieve the result of a contract call if any')
@click.argument('tx_hash', required=True)
@global_options
@online_options
def contract_call_info(tx_hash, force, wait, json_):
    print("Not yet implemented")
    return
    try:
        contract = _node_cli().Contract()
        call_object = contract.get_call_object(tx_hash)
        _print_object(call_object, "contract call object")
    except Exception as e:
        _print_error(e, exit_code=1)


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
@global_options
@online_options
@click.option('--height', type=int, default=None, help="only for accounts, retrieve an account at the specified height")
def inspect(obj, height, force, wait, json_):
    try:
        set_global_options(json_, force, wait)
        if obj.endswith(".test"):
            data = _node_cli().get_name_entry_by_name(name=obj)
            _print_object(data, title="name")
        elif obj.startswith("kh_") or obj.startswith("mh_"):
            v = _node_cli().get_block_by_hash(obj)
            _print_object(v, title="block")
        elif obj.startswith("th_"):
            v = _node_cli().get_transaction_by_hash(hash=obj)
            _print_object(v, title="transaction")
        elif obj.startswith("ak_"):
            if height is not None and height > 0:
                account = _node_cli().get_account_by_pubkey_and_height(pubkey=obj, height=height)
                _print_object(account, title=f"account at {height}")
                return
            account = _node_cli().get_account_by_pubkey(pubkey=obj)
            _print_object(account, title="account")
        elif obj.startswith("ct_"):
            v = _node_cli().get_contract(pubkey=obj)
            _print_object(v, title="contract")
        elif obj.startswith("ok_"):
            cli = _node_cli()
            data = dict(
                oracle=cli.get_oracle_by_pubkey(pubkey=obj),
                queries=cli.get_oracle_queries_by_pubkey(pubkey=obj)
            )
            _print_object(data, title="oracle context")
        elif obj.startswith("tx_"):
            v = _node_cli().verify(obj)
            _print_object(v, title="tx")
        elif obj.isdigit() and int(obj) >= 0:
            v = _node_cli().get_key_block_by_height(height=int(obj))
            _print_object(v, title="block")
        else:
            raise ValueError(f"input not recognized: {obj}")
    except Exception as e:
        _print_error(e)


#     _____ _           _
#    / ____| |         (_)
#   | |    | |__   __ _ _ _ __
#   | |    | '_ \ / _` | | '_ \
#   | |____| | | | (_| | | | | |
#    \_____|_| |_|\__,_|_|_| |_|
#
#


@cli.group(help="Interact with the blockchain")
@global_options
@online_options
def chain(json_, force, wait):
    set_global_options(json_, force, wait)
    pass


@chain.command('ttl')
@click.argument('relative_ttl', type=int)
@global_options
@online_options
def chain_ttl(relative_ttl, force, wait, json_):
    """
    Print the information of the top block of the chain.
    """
    try:
        if relative_ttl < 0:
            print("Error: the relative ttl must be a positive number")
        set_global_options(json_, force, wait)
        cli = _node_cli()
        data = cli.compute_absolute_ttl(relative_ttl)
        _print_object(data, f"ttl for node at {cli.config.api_url} ")
    except Exception as e:
        _print_error(e)


@chain.command('top')
@global_options
@online_options
def chain_top(json_, force, wait):
    """
    Print the information of the top block of the chain.
    """
    try:
        set_global_options(json_, force, wait)
        cli = _node_cli()
        data = cli.get_top_block()
        _print_object(data, f"top for node at {cli.config.api_url} ")
    except Exception as e:
        _print_error(e)


@chain.command('status')
@global_options
@online_options
def chain_status(json_, force, wait):
    """
    Print the node node status.
    """
    try:
        set_global_options(json_, force, wait)
        cli = _node_cli()
        data = cli.get_status()
        _print_object(data, f"status for node at {cli.config.api_url} ")
    except Exception as e:
        _print_error(e)


@chain.command('network-id', help="Retrieve the network id of the target node")
@global_options
@online_options
def chain_network_id(json_, force, wait):
    """
    Print the node node status.
    """
    try:
        set_global_options(json_, force, wait)
        cli = _node_cli()
        data = cli.get_status().network_id
        _print_object({"Network ID": data}, f"network id for node at {cli.config.api_url} ")
    except Exception as e:
        _print_error(e)


@chain.command('play')
@click.option('--height', type=int, help="From which height should play the chain (default top)")
@click.option('--limit', '-l', type=int, default=sys.maxsize, help="Limit the number of block to print")
@global_options
@online_options
def chain_play(height,  limit, force, wait, json_):
    """
    play the blockchain backwards
    """
    try:
        set_global_options(json_, force, wait)
        cli = _node_cli()
        g = cli.get_generation_by_height(height=height) if height is not None else cli.get_current_generation()
        # check the limit
        limit = limit if limit > 0 else 0
        while g is not None and limit > 0:
            v = g
            # if there are microblocks print the transactions
            if len(g.micro_blocks) > 0:
                txs = []
                for mb in g.micro_blocks:
                    txs.append(cli.get_micro_block_transactions_by_hash(hash=mb))
                v = {"keyblock": g.key_block, "Microblocks": txs}
            _print_object(v, title='generation')
            print('')
            limit -= 1
            if limit <= 0:
                break
            g = cli.get_generation_by_hash(hash=g.key_block.prev_key_hash)
    except Exception as e:
        _print_error(e)
        g = None
        pass


# run the client
def run():
    cli(obj={})
    exit(0)


if __name__ == "__main__":
    run()
