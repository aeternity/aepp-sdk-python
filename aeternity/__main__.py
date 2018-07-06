import logging
import click
import os
import traceback

from aeternity.epoch import EpochClient
from aeternity.config import Config, MAX_TX_TTL, ConfigException
# from aeternity.oracle import Oracle, OracleQuery, NoOracleResponse
from aeternity.signing import KeyPair
from aeternity.contract import Contract


logging.basicConfig(format='%(message)s', level=logging.INFO)


CTX_EPOCH_URL = 'EPOCH_URL'
CTX_EPOCH_URL_INTERNAL = 'EPOCH_URL_INTERNAL'
CTX_EPOCH_URL_WEBSOCKET = 'EPOCH_URL_WEBSOCKET'
CTX_KEY_PATH = 'KEY_PATH'
CTX_VERBOSE = 'VERBOSE'
CTX_QUIET = 'QUIET'


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


def _pp(data, title=None):
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
            print(f"{kv[0].ljust(30, '_')} {kv[1]}")


def _ppe(error):
    """pretty printer for errors"""
    ctx = click.get_current_context()
    print(error)
    if ctx.obj.get(CTX_VERBOSE, True):
        traceback.print_exc()


# the priority for the url selection is PARAM, ENV, DEFAULT


@click.group()
@click.pass_context
@click.version_option()
@click.option('--url', '-u', default='http://localhost:3013', envvar='EPOCH_URL', help='Epoch node url')
@click.option('--url-internal', '-i', default='http://localhost:3113', envvar='EPOCH_URL_INTERNAL')
@click.option('--url-websocket', '-w', default='ws://localhost:3013', envvar='EPOCH_URL_WEBSOCKET')
@click.option('--quiet', '-q', default=False, is_flag=True, help='Print only results')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Print verbose data')
def cli(ctx, url, url_internal, url_websocket, quiet, verbose):
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
            ("Sender account", kp.get_address()),
            ("Recipient account", recipient_account),
            ("Transaction hash", data[1])
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


@cli.group(help="Handle name lifecycle")
def name():
    pass


@name.command('info')
def name_info():
    print("info name")
    pass


@name.command('register')
def name_register():
    print("register name")
    pass


@name.command('status')
def name_status():
    print("status name")
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
@click.option("--gas", default=1000, help='amount of gas to deploy the contract')
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
    _pp([
        ('Block hash', data.hash),
        ('Block height', data.height),
        ('Miner', data.miner),
        ('Transactions', len(data.transactions)),
    ])
    for t in data.transactions:
        print("> ", t.get("hash"))


@inspect.command('height', help='The height of the chain to inspect (eg: 14352)')
@click.argument('chain_height', default=1)
def inspect_block(chain_height):
    data = _epoch_cli().get_block_by_height(chain_height)
    _pp([
        ('Block hash', data.hash),
        ('Block height', data.height),
        ('Miner', data.miner),
        ('Transactions', len(data.transactions)),
    ])
    for t in data.transactions:
        print("> ", t.get("hash"))


@inspect.command('transaction', help='The transaction hash to inspect (eg: th$...)')
@click.argument('tx_hash')
def inspect_transaction(tx_hash):
    _check_prefix(tx_hash, "th")
    data = _epoch_cli().get_transaction_by_transaction_hash(tx_hash, tx_encoding='json')
    _pp([
        ('Block hash', data.transaction['block_hash']),
        ('Block height', data.transaction['block_height']),
        ('Block hash', data.transaction['block_hash']),
        ('Signatures', data.transaction['signatures']),
        ('Sender account', data.transaction['tx']['sender']),
        ('Recipient account', data.transaction['tx']['recipient']),
        ('Amount', data.transaction['tx']['amount']),
        ('TTL', data.transaction['tx']['ttl'])
    ])


@inspect.command('account', help='The address of the account to inspect (eg: ak$...)')
@click.argument('account')
def inspect_account(account):
    _check_prefix(account, "ak")
    try:
        data = _epoch_cli().get_balance(account)
        _pp(("Account balance", data))
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


@chain.command('height')
def chain_height():
    data = _epoch_cli().get_height()
    _pp(("Chain block height", data))


@chain.command('version')
def chain_version():
    data = _epoch_cli().get_version()
    _pp(("Epoch node version", data))



# run the client
cli(obj={})
exit(0)


# ___   _____     ______     ______   _________  _____  _____  ________  ________
# .'   `.|_   _|   |_   _ `. .' ____ \ |  _   _  ||_   _||_   _||_   __  ||_   __  |
# /  .-.  \ | |       | | `. \| (___ \_||_/ | | \_|  | |    | |    | |_ \_|  | |_ \_|
# | |   | | | |   _   | |  | | _.____`.     | |      | '    ' |    |  _|     |  _|
# \  `-'  /_| |__/ | _| |_.' /| \____) |   _| |_      \ \__/ /    _| |_     _| |_
# `.___.'|________||______.'  \______.'  |_____|      `.__.'    |_____|   |_____|


# def print_usage():
#     print('''aeternity cli tool:
# Usage:
#     balance [pubkey]
#         Returns the balance of pubkey or the balance of the node's pubkey
#     height
#         returns the top block number
#     generate wallet <path> [--password <password>]
#         creates a new wallet
#     spend <amount> <receipient> <wallet-path> [--password <password>]
#         send money to another account. The folder at wallet-path must contain
#         key and key.pub
#     wallet info <wallet-path>
#         prints info about your wallet (address in base58)
#     inspect block <block height | block hash | "latest">
#         prints the contents of a block
#     inspect transaction <transaction hash>
#         prints the contents of a transaction
#     name available <domain.aet>
#             Check Domain availablity
#     name register <domain.aet> <wallet-path> [--force]
#             Register a domain for the given account (incurs fees!)
#     name status <domain.aet>
#             Checks the status of a domain
#     name update <domain.aet> <address>
#             Updates where the name points to
#     name revoke <domain.aet> [--force]
#             Removes this domain from the block chain (incurs fees!)
#     name transfer <domain.aet> <receipient_address> [--force]
#             Transfers a domain to another user

#     oracle register [--query-format] [--response-format] [--default-query-fee]
#                     [--default-fee] [--default-ttl] [--default-query-ttl]
#                     [--default-response-ttl]
#             You will be prompted for any non-provided argument
#     oracle query [--oracle-pubkey] [--query-fee] [--query-ttl] [--response-ttl]
#                  [--fee]
#             You will be prompted for any non-provided argument

# The `--force` will suppress any questions before performing the action.

# You can override the standard connection ports using the following environment
# variables:
#     AE_EXTERNAL_HOST, AE_EXTERNAL_PORT, AE_INTERNAL_HOST, AE_INTERNAL_PORT,
#     AE_WEBSOCKET_HOST and AE_WEBSOCKET_PORT
# or using the command line parameters:
#     --external-host
#     --internal-host
#     --websocket-host

# When running against a local setup of Epoch based on the provided
# docker-compose setup, specify --docker for the right URLs to be formed.
# ''')
#     sys.exit(1)


# def stderr(*args):
#     for message in args:
#         sys.stderr.write(message)
#         sys.stderr.write(' ')
#     sys.stderr.write('\n')
#     sys.stderr.flush()


# def prompt(message, skip):
#     if skip:
#         return True
#     if input(message + ' [y/N]') != 'y':
#         print('cancelled')
#         sys.exit(0)


# args = sys.argv[1:]

# if '--help' in args or len(args) < 1:
#     print_usage()


# _no_popargs_default = object()


# def popargs(d, key, default=_no_popargs_default, boolean=False):
#     try:
#         idx = d.index(key)
#         d.pop(idx)  # remove arg
#         if boolean:
#             return True
#         else:
#             return d.pop(idx)  # remove value after arg
#     except ValueError:
#         if default != _no_popargs_default:
#             return default
#         elif boolean:
#             return False
#         else:
#             raise


# external_host = popargs(args, '--external-host', None)
# internal_host = popargs(args, '--internal-host', None)
# websocket_host = popargs(args, '--websocket-host', None)
# docker = popargs(args, '--docker', False, True)
# verbose = popargs(args, '--verbose', False, True)

# if verbose:
#     logging.getLogger().setLevel(logging.DEBUG)

# config = Config(
#     external_host=external_host,
#     internal_host=internal_host,
#     websocket_host=websocket_host,
#     docker_semantics=docker
# )

# client = EpochClient(configs=config)


# main_arg = args[0]


# def aens(args, force=False):
#     command = args[1]
#     domain = args[2]
#     try:
#         AEName.validate_name(domain)
#     except AENSException as exc:
#         stderr('Error:', str(exc))
#         sys.exit(1)

#     name = AEName(domain)

#     if command == 'available':
#         if name.is_available():
#             print(f'{domain} is available')
#             sys.exit(0)
#         else:
#             print(f'{domain} is not available')
#             sys.exit(1)

#     if command == 'register':
#         if not name.is_available():
#             print('Name was already claimed')
#             sys.exit(1)
#         wallet_path = args[3]
#         keypair = read_keypair(wallet_path)
#         prompt('Do you want to register this name? (incurs fees)', skip=force)
#         print('Name is available, pre-claiming now')
#         name.preclaim(keypair)
#         print('Pre-Claim successful')
#         print('Claiming name (waiting for next block, this may take a while)')
#         name.claim_blocking(keypair)
#         print('Claim successful')
#         print(f'{domain} was registered successfully')
#         sys.exit(0)

#     if command == 'status':
#         name.update_status()
#         print('status: %s' % name.status)
#         print('name_hash: %s' % name.b58_name)
#         print('name_ttl: %s' % name.name_ttl)
#         print('pointers: %s' % name.pointers)
#         sys.exit(0)

#     if command == 'update':
#         try:
#             address = args[3]
#         except IndexError:
#             print('Missing parameter <address>')
#             sys.exit(1)
#         try:
#             name.validate_pointer(address)
#         except ValueError:
#             print(
#                 'Invalid address\n'
#                 '(note: make sure to wrap the address in single quotes on the shell)'
#             )
#             sys.exit(1)
#         name.update_status()
#         name.update(target=address)
#         print(
#             f'Updated {domain} to point to "{address[:8]}..." '
#             '(update will take one block time interval to propagate)'
#         )
#         sys.exit(0)

#     if command == 'revoke':
#         prompt('Do really want to revoke this name? (incurs fees)', skip=force)
#         name.revoke()

#     if command == 'transfer':
#         try:
#             receipient = args[3]
#         except IndexError:
#             print('Missing parameter <receipient_address>')
#             sys.exit(1)

#         try:
#             name.validate_pointer(receipient)
#         except Exception:
#             print(
#                 'Invalid parameter for <receipient_address>\n'
#                 '(note: make sure to wrap the address in single quotes on the shell)'
#             )
#             sys.exit(1)

#         prompt('Do really want to transfer this name?', skip=force)
#         name.transfer_ownership(receipient)


# class CLIOracle(Oracle):
#     def get_response(self, message):
#         print(f'Received message:\n{message}')
#         print('Please type a json response:')
#         json_data = None
#         while json_data is None:
#             try:
#                 return json.loads(input('JSON: '))
#             except KeyboardInterrupt:
#                 print('Cancelled, oracle will not respond to query.')
#                 raise NoOracleResponse()
#             except Exception:
#                 print('Invalid JSON. Please retry or press ctrl-c to cancel')


# class CLIOracleQuery(OracleQuery):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.response_received = False
#         self.last_response = None

#     def on_response(self, response, query):
#         self.response_received = True
#         self.last_response = response


# def cli_args_to_kwargs(cli_args, args):
#     return {
#         # this requires the kwargs to be compatible to the CLI params
#         cli_arg[2:].replace('-', '_'): args.get(cli_arg, None)
#         for cli_arg in cli_args
#     }


# def oracle(args, force=False):
#     '''
#     :param args:
#     :param force:
#     :return:
#     '''

#     command, args = args[0], args[1:]

#     if command == 'register':
#         cli_args = [
#             '--query-format',
#             '--response-format',
#             '--default-query-fee',
#             '--default-fee',
#             '--default-ttl',
#             '--default-query-ttl',
#             '--default-response-ttl',
#         ]
#         mapped_kwargs = cli_args_to_kwargs(cli_args, args)
#         oracle = CLIOracle(**mapped_kwargs)
#         client.mount(oracle)
#         client.listen()
#     elif command == 'query':
#         cli_args = [
#             '--oracle-pubkey',
#             '--query-fee',
#             '--query-ttl',
#             '--response-ttl',
#             '--fee',
#         ]
#         mapped_kwargs = cli_args_to_kwargs(cli_args, args)
#         oracle_query = CLIOracleQuery(**mapped_kwargs)
#         client.mount(oracle_query)
#         fee = int(mapped_kwargs['query_fee'])
#         print(
#             f'Please enter a query to be sent. Note: every query will '
#             f'cost a fee of {fee}! Cancel with ctrl-c'
#         )
#         while True:
#             try:
#                 query = json.loads(input('Query:\n'))
#                 oracle_query.query(query)
#                 print('You query was sent, waiting for reply from oracle. Press ctrl-c to stop waiting.')
#                 client.listen_until(lambda: oracle_query.response_received)
#                 print('Received response:')
#                 print(oracle_query.last_response)
#                 print('You can enter another query now or cancel with ctrl-c.')
#             except KeyboardInterrupt:
#                 print('Interrupted by user')
#                 sys.exit(1)
#             except Exception:
#                 print('Invalid json-query, please try again (ctrl-c to exit)')
#     else:
#         stderr('Unknown oracle command: %s' % command)
#         sys.exit(1)


# def balance(args):
#     if len(args) >= 2:
#         pubkey = args[1]
#     else:
#         pubkey = client.get_pubkey()
#     try:
#         balance = client.get_balance(pubkey)
#         print(balance)
#     except AException as exc:
#         stderr(f'Error getting balance: {exc.payload}')


# def height():
#     print(client.get_height())


# def read_keypair(wallet_path, password=None):
#     if not os.path.exists(wallet_path):
#         stderr(f'Path to wallet "{wallet_path}" does not exist!')
#         sys.exit(1)
#     if password is None:
#         password = getpass('Wallet password: ')
#     keypair = KeyPair.read_from_dir(wallet_path, password)
#     return keypair


# @contextmanager
# def handle_connection_failure():
#     try:
#         yield
#     except requests.exceptions.ConnectionError:
#         print('Unable to connect to node')
#         sys.exit(1)


# # allow using the --force parameter anywhere
# force = False
# if '--force' in args:
#     args.remove('--force')
#     force = True

# if main_arg == 'name':
#     aens(args, force=force)
# elif main_arg == 'oracle':
#     oracle(args, force=force)
# elif main_arg == 'balance':
#     balance(args)
# elif main_arg == 'height':
#     height()
# elif main_arg == 'spend':
#     password = popargs(args, '--password', None)
#     if len(args) != 4:
#         print('You must specify <amount>, <receipient> and <wallet-path>. '
#               'Tip: escape the receipient address in single quotes to make '
#               'sure that your shell does not get confused with the dollar-sign')
#         sys.exit(1)
#     if password is None:
#         password = getpass('Wallet password: ')
#     amount, receipient, wallet_path = args[1:]
#     amount = int(amount)
#     if amount < 0:
#         print('Invalid amount')
#         sys.exit(1)
#     keypair = KeyPair.read_from_dir(wallet_path, password)
#     with handle_connection_failure():
#         response, tx_hash = EpochClient().spend(keypair, receipient, amount)
#     if response == {}:
#         print(
#             'An error occurred, your transaction was not completed. Please check'
#             'the logs of the node to diagnose the problem.'
#         )
#         sys.exit(1)

#     print(
#         'Transaction sent. Your balance will change once it is included in '
#         'the blockchain.'
#     )
#     print(f'TxHash: {tx_hash}')
#     sys.exit(0)
# elif main_arg == 'generate':
#     # args[1] is the string 'wallet'
#     password = popargs(args, '--password', None)
#     if password is None:
#         print('DO NOT LOSE THE PASSWORD YOU ARE GOING TO TYPE NOW FOR YOUR'
#               'WALLET. LOSING THIS PASSWORD WILL RESULT IN LOSING ACCESS TO YOUR'
#               'WALLET, AND ALL ASSOCIATED ENTITIES (NAMES, TOKENS, ORACLE AND FUNDS)!')
#         password = getpass('New Wallet password: ')
#     keypair = KeyPair.generate()
#     try:
#         path = args[2]
#     except ValueError:
#         print('You must specify the <path> argument')
#         sys.exit(1)
#     keypair.save_to_folder(path, password)
#     address = keypair.get_address()
#     print('Your wallet has been generated:')
#     print('Address: %s' % address)
#     print('Saved to: %s' % path)
# elif main_arg == 'wallet':
#     if args[1] == 'info':
#         wallet_path = args[2]
#         password = popargs(args, '--password', None)
#         keypair = read_keypair(wallet_path, password)
#         print('Address: %s' % keypair.get_address())
#     else:
#         stderr('Unknown command')
#         sys.exit(1)
# elif main_arg == 'inspect':
#     inspect_what = args[1]
#     if inspect_what == 'block':
#         block_id = args[2]
#         if block_id == 'latest':
#             block = client.get_latest_block()
#         elif block_id.startswith('bh$'):
#             block = client.get_block_by_hash(block_id)
#         else:
#             block = client.get_block_by_height(block_id)
#         print(block)
#     elif inspect_what == 'transaction' or inspect_what == 'tx':
#         transaction_hash = args[2]
#         if not transaction_hash.startswith('th$'):
#             stderr('A transaction hash must start with "th$"')
#             sys.exit(1)
#         transaction = client.get_transaction_by_transaction_hash(transaction_hash)
#         print(transaction)
#     else:
#         stderr('Can only inspect `block`.')
#         sys.exit(1)
# else:
#     print(f'Invalid args. Use --help to see available commands and arguments')
#     sys.exit(1)
