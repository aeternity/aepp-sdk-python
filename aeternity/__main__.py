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
The `--force` will suppress any questions before performing the action.

You can override the standard connection ports using the following environment
variables: AE_LOCAL_PORT, AE_LOCAL_INTERNAL_PORT and AE_WEBSOCKET

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

client = EpochClient()

system, command = args[:2]

# allow using the --force parameter anywhere
noinput = False
if '--force' in args:
    args.remove('--force')
    noinput = True

if system == 'aens':
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
        prompt('Do you want to register this name? (incurs fees)', skip=noinput)
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
        prompt('Do really want to revoke this name? (incurs fees)', skip=noinput)
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

        prompt('Do really want to transfer this name?', skip=noinput)
        name.transfer_ownership(receipient)
