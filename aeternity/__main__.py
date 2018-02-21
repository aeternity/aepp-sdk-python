import json
import sys

from aeternity import EpochClient, AEName, AENSException, Oracle, Config
from aeternity.oracle import NoOracleResponse, OracleQuery


def print_usage():
    print('''aeternity cli tool:
Usage:

    aens available <domain.aet>
            Check Domain availablity    
    aens register <domain.aet> [--force]
            Register a domain (incurs fees!)    
    aens status <domain.aet>
            Checks the status of a domain    
    aens update <domain.aet> <address>
            Updates where the name points to    
    aens revoke <domain.aet> [--force]
            Removes this domain from the block chain (incurs fees!)    
    aens transfer <domain.aet> <receipient_address> [--force]
            Transfers a domain to another user
    
    oracle register [--query-format] [--response-format] [--default-query-fee]
                    [--default-fee] [--default-ttl] [--default-query-ttl]
                    [--default-response-ttl]
            You will be prompted for any non-provided argument
    
    oracle query [--oracle-pubkey] [--query-fee] [--query-ttl] [--response-ttl]
                 [--fee]
            You will be prompted for any non-provided argument
 
The `--force` will suppress any questions before performing the action.

You can override the standard connection ports using the following environment
variables: AE_LOCAL_PORT, AE_LOCAL_INTERNAL_PORT and AE_WEBSOCKET, or using
the parameters: --external-port, --internal-port and --websocket-port

''')
    sys.exit(1)

def stderr(*args):
    for message in args:
        sys.stderr.write(message)
        sys.stderr.write(' ')
    sys.stderr.write('\n')
    sys.stderr.flush()


def prompt(message, skip):
    if skip:
        return True
    if input(message + ' [y/N]') != 'y':
        print('cancelled')
        sys.exit(0)

args = sys.argv[1:]

if '--help' in args:
    print_usage()

if len(args) < 2:
    print_usage()


def popdefault(d, key, default):
    try:
        d.pop(key)
    except KeyError:
        return default

external_port = popdefault(args, '--external-port', None)
internal_port = popdefault(args, '--internal-port', None)
websocket_port = popdefault(args, '--websocket-port', None)

config = Config(
    local_port=external_port,
    internal_port=internal_port,
    websocket_port=websocket_port,
)

client = EpochClient(config=config)

system = args[0]

def aens(args, force=False):
    command = args[1]
    domain = args[2]
    try:
        AEName.validate_name(domain)
    except AENSException as exc:
        stderr('Error:', str(exc))
        sys.exit(1)

    name = AEName(domain)

    if command == 'available':
        if name.is_available():
            print(f'{domain} is available')
            sys.exit(0)
        else:
            print(f'{domain} is not available')
            sys.exit(1)

    if command == 'register':
        if not name.is_available():
            print('Name was already claimed')
            sys.exit(1)
        prompt('Do you want to register this name? (incurs fees)', skip=force)
        print('Name is available, pre-claiming now')
        name.preclaim()
        print('Pre-Claim successful')
        print('Claiming name (waiting for next block, this may take a while)')
        name.claim_blocking()
        print('Claim successful')
        print(f'{domain} was registered successfully')
        sys.exit(0)

    if command == 'status':
        name.update_status()
        print('status: %s' % name.status)
        print('name_hash: %s' % name.name_hash)
        print('name_ttl: %s' % name.name_ttl)
        print('pointers: %s' % name.pointers)
        sys.exit(0)

    if command == 'update':
        try:
            address = args[3]
        except IndexError:
            print('Missing parameter <address>')
            sys.exit(1)
        try:
            name.validate_pointer(address)
        except ValueError:
            print(
                'Invalid address\n'
                '(note: make sure to wrap the address in single quotes on the shell)'
            )
            sys.exit(1)
        name.update_status()
        name.update(target=address)
        print(
            f'Updated {domain} to point to "{address[:8]}..." '
            '(update will take one block time interval to propagate)'
        )
        sys.exit(0)

    if command == 'revoke':
        prompt('Do really want to revoke this name? (incurs fees)', skip=force)
        name.revoke()

    if command == 'transfer':
        try:
            receipient = args[3]
        except IndexError:
            print('Missing parameter <receipient_address>')
            sys.exit(1)

        try:
            name.validate_pointer(receipient)
        except:
            print(
                'Invalid parameter for <receipient_address>\n'
                '(note: make sure to wrap the address in single quotes on the shell)'
            )
            sys.exit(1)

        prompt('Do really want to transfer this name?', skip=force)
        name.transfer_ownership(receipient)


class CLIOracle(Oracle):
    def get_response(self, message):
        print(f'Received message:\n{message}')
        print('Please type a json response:')
        json_data = None
        while json_data is None:
            try:
                return json.loads(input('JSON: '))
            except KeyboardInterrupt:
                print('Cancelled, oracle will not respond to query.')
                raise NoOracleResponse()
            except:
                print('Invalid JSON. Please retry or press ctrl-c to cancel')


def cli_args_to_kwargs(cli_args, args):
    return {
        # this requires the kwargs to be compatible to the CLI params
        cli_arg[2:].replace('-', '_'): args.get(cli_arg, None)
        for cli_arg in cli_args
    }


def oracle(args, force=False):
    '''
    :param args:
    :param force:
    :return:
    '''

    command, args = args[0], args[1:]

    if command == 'register':
        cli_args = [
            '--query-format',
            '--response-format',
            '--default-query-fee',
            '--default-fee',
            '--default-ttl',
            '--default-query-ttl',
            '--default-response-ttl',
        ]
        mapped_kwargs = cli_args_to_kwargs(cli_args, args)
        oracle = CLIOracle(**mapped_kwargs)
        client.mount(oracle)
        client.listen()
    elif command == 'query':
        cli_args = [
            '--oracle-pubkey',
            '--query-fee',
            '--query-ttl',
            '--response-ttl',
            '--fee',
        ]
        mapped_kwargs = cli_args_to_kwargs(cli_args, args)
        oracle_query = OracleQuery(**mapped_kwargs)
        client.mount(oracle_query)


# allow using the --force parameter anywhere
force = False
if '--force' in args:
    args.remove('--force')
    force = True

if system == 'aens':
    aens(args, force=force)
elif system == 'oracle':
    oracle(args, force=force)
else:
    print(f'Invalid system "{system}"')
    sys.exit(1)
