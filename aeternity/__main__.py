import logging
import click
import os
import json
import sys

from aeternity import __version__

from aeternity.epoch import EpochClient
# from aeternity.oracle import Oracle, OracleQuery, NoOracleResponse
from . import utils, signing, aens, config
from aeternity.contract import Contract

from datetime import datetime, timezone


logging.basicConfig(format='%(message)s', level=logging.INFO)


CTX_EPOCH_URL = 'EPOCH_URL'
CTX_EPOCH_URL_DEBUG = 'EPOCH_URL_DEBUG'
CTX_KEY_PATH = 'KEY_PATH'
CTX_QUIET = 'QUIET'
CTX_AET_DOMAIN = 'AET_NAME'
CTX_FORCE_COMPATIBILITY = 'CTX_FORCE_COMPATIBILITY'
CTX_BLOCKING_MODE = 'CTX_BLOCKING_MODE'
CTX_OUTPUT_JSON = 'CTX_OUTPUT_JSON'


def _epoch_cli():
    try:
        ctx = click.get_current_context()
        # set the default configuration
        url = ctx.obj.get(CTX_EPOCH_URL)
        url_i = ctx.obj.get(CTX_EPOCH_URL_DEBUG)
        url_i = url_i if url_i is not None else url
        config.Config.set_defaults(config.Config(
            external_url=url,
            internal_url=url_i,
            force_compatibility=ctx.obj.get(CTX_FORCE_COMPATIBILITY)
        ))
    except config.ConfigException as e:
        print("Configuration error: ", e)
        exit(1)
    except config.UnsupportedEpochVersion as e:
        print(e)
        exit(1)

    # load the epoch client
    return EpochClient(blocking_mode=ctx.obj.get(CTX_BLOCKING_MODE))


def _account(keystore_name, password=None):
    """
    utility function to get the keypair from the click context
    :return: (keypair, keypath)
    """
    ctx = click.get_current_context()
    kf = ctx.obj.get(CTX_KEY_PATH) if keystore_name is None else keystore_name
    if not os.path.exists(kf):
        print(f'Key file {kf} does not exits.')
        exit(1)
    try:
        if password is None:
            password = click.prompt("Enter the account password", default='', hide_input=True)
        return signing.Account.load_from_keystore(kf, password), os.path.abspath(kf)
    except Exception:
        print("Invalid password")
        exit(1)


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
    else:
        if label.lower() == "time":
            value = datetime.fromtimestamp(value / 1000, timezone.utc).isoformat('T')
        _pl(label, offset, value=value)


def _print_object(data, title=None):
    ctx = click.get_current_context()

    if ctx.obj.get(CTX_OUTPUT_JSON, False):
        if isinstance(data, tuple):
            print(json.dumps(data._asdict(), indent=2))
            return
        if isinstance(data, str):
            print(data)
            return
        print(json.dumps(data, indent=2))
        return

    _po(title, data)


# Commands
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# set global options TODO: this is a bit silly, we should probably switch back to stdlib
_global_options = [
    click.option('--force', is_flag=True, default=False, help='Ignore epoch version compatibility check'),
    click.option('--wait', is_flag=True, default=False, help='Wait for transactions to be included'),
    click.option('--json', 'json_', is_flag=True, default=False, help='Print output in JSON format'),
]

_account_options = [
    click.option('--password', default=None, help="Read account password from stdin [WARN: this method is not secure]")
]


def global_options(func):
    for option in reversed(_global_options):
        func = option(func)
    return func


def account_options(func):
    func = global_options(func)
    for option in reversed(_account_options):
        func = option(func)
    return func


def set_global_options(force, wait, json_):
    ctx = click.get_current_context()
    ctx.obj[CTX_FORCE_COMPATIBILITY] = force
    ctx.obj[CTX_BLOCKING_MODE] = wait
    ctx.obj[CTX_OUTPUT_JSON] = json_

# the priority for the url selection is PARAM, ENV, DEFAULT


@click.group()
@click.pass_context
@click.version_option()
@click.option('--url', '-u', default='https://sdk-testnet.aepps.com', envvar='EPOCH_URL', help='Epoch node url', metavar='URL')
@click.option('--debug-url', '-d', default=None, envvar='EPOCH_URL_DEBUG', metavar='URL')
@global_options
@click.version_option(version=__version__)
def cli(ctx, url, debug_url, force, wait, json_):
    """
    Welcome to the aecli client.

    The client is to interact with an epoch node.

    """
    ctx.obj[CTX_EPOCH_URL] = url
    ctx.obj[CTX_EPOCH_URL_DEBUG] = debug_url
    set_global_options(force, wait, json_)


@cli.command('config', help="Print the client configuration")
@click.pass_context
def config_cmd(ctx):
    _print_object({
        "Epoch URL": ctx.obj.get(CTX_EPOCH_URL),
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
@click.option('--overwrite', default=False, is_flag=True, help="Overwrite existing keys without asking")
@account_options
def account_create(keystore_name, password, overwrite, force, wait, json_):
    try:
        set_global_options(force, wait, json_)
        new_account = signing.Account.generate()
        # TODO: introduce default configuration path
        if not overwrite and os.path.exists(keystore_name):
            click.confirm(f'Keystore file {keystore_name} already exists, overwrite?', abort=True)
        if password is None:
            password = click.prompt("Enter the account password", default='', hide_input=True)
        new_account.save_to_keystore_file(keystore_name, password)
        _print_object({
            'Account address': new_account.get_address(),
            'Account path': os.path.abspath(keystore_name)
        }, title='Account created')
    except Exception as e:
        print(e)


@account.command('save', help='Save a private keys string to a password protected file account')
@click.argument('keystore_name', required=True)
@click.argument('private_key', required=True)
@click.option('--overwrite', default=False, is_flag=True, help="Overwrite existing keys without asking")
@account_options
def account_save(keystore_name, private_key, password, overwrite, force, wait, json_):
    try:
        set_global_options(force, wait, json_)
        account = signing.Account.from_private_key_string(private_key)
        if not overwrite and os.path.exists(keystore_name):
            click.confirm(f'Keystore file {keystore_name} already exists, overwrite?', abort=True)
        if password is None:
            password = click.prompt("Enter the account password", default='', hide_input=True)
        account.save_to_keystore_file(keystore_name, password)
        _print_object({
            'Account address': account.get_address(),
            'Account path': os.path.abspath(keystore_name)
        }, title='Account saved')
    except Exception as e:
        print(e)


@account.command('address', help="Print the account address (public key)")
@click.argument('keystore_name')
@click.option('--private-key', is_flag=True, help="Print the private key instead of the account address")
@account_options
def account_address(password, keystore_name, private_key, force, wait, json_):
    try:
        set_global_options(force, wait, json_)
        account, keystore_path = _account(keystore_name, password=password)
        o = {'Account address': account.get_address()}
        if private_key:
            click.confirm(f'!Warning! this will print your private key on the screen, are you sure?', abort=True)
            o["Private key"] = account.get_private_key()
        _print_object(o)
    except Exception as e:
        print(e)


@account.command('balance', help="Get the balance of a account")
@click.argument('keystore_name')
@account_options
def account_balance(keystore_name, password, force, wait, json_):
    try:
        set_global_options(force, wait, json_)
        account, _ = _account(keystore_name, password=password)
        account = _epoch_cli().get_account_by_pubkey(pubkey=account.get_address())
        _print_object(account)
    except Exception as e:
        print(e)


@account.command('spend', help="Create a transaction to another account")
@click.argument('keystore_name', required=True)
@click.argument('recipient_id', required=True)
@click.argument('amount', required=True, type=int)
@click.option('--ttl', default=config.DEFAULT_TX_TTL, help="Validity of the spend transaction in number of blocks (default forever)")
@account_options
def account_spend(keystore_name, recipient_id, amount, ttl, password, force, wait, json_):
    try:
        set_global_options(force, wait, json_)
        account, keystore_path = _account(keystore_name, password=password)
        if not utils.is_valid_hash(recipient_id, prefix="ak"):
            raise ValueError("Invalid recipient address")
        _, signature, tx_hash = _epoch_cli().spend(account, recipient_id, amount, tx_ttl=ttl)
        _print_object({
            "Transaction hash": tx_hash,
            "Signature": signature,
            "Sender account": account.get_address(),
            "Recipient account": recipient_id,
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


@cli.group(help="Handle name lifecycle")
def name():
    pass


@name.command('claim', help="Claim a domain name")
@click.argument('keystore_name', required=True)
@click.argument('domain', required=True)
@click.option("--name-ttl", default=config.DEFAULT_NAME_TTL, help=f'Lifetime of the claim in blocks (default {config.DEFAULT_NAME_TTL})')
@click.option("--ttl", default=config.DEFAULT_TX_TTL, help=f'Lifetime of the claim request in blocks (default {config.DEFAULT_TX_TTL})')
@account_options
def name_register(keystore_name, domain, name_ttl, ttl, password, force, wait, json_):
    try:
        set_global_options(force, wait, json_)
        account, _ = _account(keystore_name, password=password)
        name = _epoch_cli().AEName(domain)
        name.update_status()
        if name.status != aens.AEName.Status.AVAILABLE:
            print("Domain not available")
            exit(0)
        txs = name.full_claim_blocking(account, name_ttl=name_ttl, tx_ttl=ttl)
        _print_object(txs, title=f"Name {domain} claimed")
    except ValueError as e:
        print(e)


@name.command('update')
@click.argument('keystore_name', required=True)
@click.argument('domain', required=True)
@click.argument('address', required=True)
@click.option("--name-ttl", default=100, help=f'Lifetime of the claim in blocks (default {config.DEFAULT_NAME_TTL})')
@click.option("--ttl", default=100, help=f'Lifetime of the claim request in blocks (default {config.DEFAULT_TX_TTL})')
@account_options
def name_update(keystore_name, domain, address, name_ttl, ttl, password, force, wait, json_):
    """
    Update a name pointer
    """
    try:
        set_global_options(force, wait, json_)
        account, _ = _account(keystore_name, password=password)
        name = _epoch_cli().AEName(domain)
        name.update_status()
        if name.status != name.Status.CLAIMED:
            print(f"Domain is {name.status} and cannot be transferred")
            exit(0)
        _, signature, tx_hash = name.update(account, target=address, name_ttl=name_ttl, tx_ttl=ttl)
        _print_object({
            "Transaction hash": tx_hash,
            "Signature": signature,
            "Sender account": account.get_address(),
            "Target ID": address
        }, title=f"Name {domain} status update")
    except Exception as e:
        print(e)


@name.command('revoke', help="Revoke a claimed name")
@click.argument('keystore_name', required=True)
@click.argument('domain', required=True)
@account_options
def name_revoke(keystore_name, domain, password, force, wait, json_):
    try:
        set_global_options(force, wait, json_)
        account, _ = _account(keystore_name, password=password)
        name = _epoch_cli().AEName(domain)
        name.update_status()
        if name.status == name.Status.AVAILABLE:
            print("Domain is available, nothing to revoke")
            exit(0)
        _, signature, tx_hash = name.revoke(account)
        _print_object({
            "Transaction hash": tx_hash,
            "Signature": signature,
            "Sender account": account.get_address(),
        }, title=f"Name {domain} status revoke")
    except Exception as e:
        pass


@name.command('transfer', help="Transfer a claimed domain to another account")
@click.argument('keystore_name', required=True)
@click.argument('domain', required=True)
@click.argument('address')
@account_options
def name_transfer(keystore_name, domain, address, password, force, wait, json_):
    """
    Transfer a name to another account
    """
    try:
        set_global_options(force, wait, json_)
        account, _ = _account(keystore_name, password=password)
        name = _epoch_cli().AEName(domain)
        name.update_status()
        if name.status != name.Status.CLAIMED:
            print(f"Domain is {name.status} and cannot be transferred")
            exit(0)
        _, signature, tx_hash = name.transfer_ownership(account, address)
        _print_object({
            "Transaction hash": tx_hash,
            "Signature": signature,
            "Sender account": account.get_address(),
            "Target ID": address
        }, title=f"Name {domain} status transfer to {address}")
    except Exception as e:
        print(e)


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

@click.group('contract', help='Deploy and execute contracts on the chain')
def contract():
    pass


@contract.command(help="Compile a contract")
@click.argument("contract_file")
def contract_compile(contract_file):
    try:
        with open(contract_file) as fp:
            code = fp.read()
            c = _epoch_cli().Contract(Contract.SOPHIA)
            result = c.compile(code)
            _print_object({"bytecode", result})
    except Exception as e:
        print(e)


@contract.command('deploy', help='Deploy a contract on the chain')
@click.argument('keystore_name', required=True)
@click.argument("contract_file", required=True)
@click.option("--gas", default=config.CONTRACT_DEFAULT_GAS, help='Amount of gas to deploy the contract')
@account_options
def contract_deploy(keystore_name, contract_file, gas, password, force, wait, json_):
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
            set_global_options(force, wait, json_)
            account, _ = _account(keystore_name, password=password)
            code = fp.read()
            contract = _epoch_cli().Contract(code)
            tx = contract.tx_create(account, gas=gas)
            # save the contract data
            contract_data = {
                'source': contract.source_code,
                'bytecode': contract.bytecode,
                'address': contract.address,
                'transaction': tx.tx_hash,
                'owner': account.get_address(),
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
@click.argument('keystore_name', required=True)
@click.argument("deploy_descriptor", required=True)
@click.argument("function", required=True)
@click.argument("params", required=True)
@click.argument("return_type", required=True)
@click.option("--gas", default=config.CONTRACT_DEFAULT_GAS, help='Amount of gas to deploy the contract')
@account_options
def contract_call(keystore_name, deploy_descriptor, function, params, return_type, gas,  password, force, wait, json_):
    try:
        with open(deploy_descriptor) as fp:
            contract = json.load(fp)
            source = contract.get('source')
            bytecode = contract.get('bytecode')
            address = contract.get('address')

            set_global_options(force, wait, json_)
            account, _ = _account(keystore_name, password=password)

            contract = _epoch_cli().Contract(source, bytecode=bytecode, address=address)
            result = contract.tx_call(account, function, params, gas=gas)
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
@global_options
def inspect(obj, force, wait, json_):
    try:
        set_global_options(force, wait, json_)
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
        elif obj.startswith("ct_"):
            v = _epoch_cli().get_contract(pubkey=obj)
            _print_object(v)
        elif obj.isdigit() and int(obj) >= 0:
            v = _epoch_cli().get_key_block_by_height(height=int(obj))
            _print_object(v)
        else:
            raise ValueError(f"input not recognized: {obj}")
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
@global_options
def chain(force, wait, json_):
    set_global_options(force, wait, json_)
    pass


@chain.command('top')
@global_options
def chain_top(force, wait, json_):
    """
    Print the information of the top block of the chain.
    """
    set_global_options(force, wait, json_)
    data = _epoch_cli().get_top_block()
    _print_object(data)


@chain.command('status')
@global_options
def chain_status(force, wait, json_):
    """
    Print the epoch node status.
    """
    set_global_options(force, wait, json_)
    data = _epoch_cli().get_status()
    _print_object(data)


@chain.command('play')
@click.option('--height', type=int, help="From which height should play the chain (default top)")
@click.option('--limit', '-l', type=int, default=sys.maxsize, help="Limit the number of block to print")
@global_options
def chain_play(height,  limit, force, wait, json_):
    """
    play the blockchain backwards
    """
    try:
        set_global_options(force, wait, json_)
        cli = _epoch_cli()
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
            g = cli.get_generation_by_hash(hash=g.key_block.get("prev_key_hash"))
    except Exception as e:
        print(e)
        g = None
        pass


# run the client
cli(obj={})
exit(0)
