import pytest
from pytest import raises

from aeternity.contract import ContractError, Contract
from aeternity import hashing, utils

test_sophia_contract = '''
contract SimpleStorage =
  record state = { data : int }
  function init(value : int) : state = { data = value }
  function get() : int = state.data
  function set(value : int) = put(state{data = value})
'''

broken_contract = '''
contract Identity =
  BROKEN state = ()
  function main(x : int) = x
'''

#
# SOPHIA
#


def _sophia_contract_tx_create_online(node_cli, account, compiler_fixture):
    # runt tests
    compiled_contract = compiler_fixture.COMPILER.compile(test_sophia_contract)
    node_cli.Contract(bytecode=compiled_contract)
    #
    contract = node_cli.Contract(test_sophia_contract)
    contract.tx_create(account, gas=100000)
    assert contract.address is not None
    assert len(contract.address) > 0
    assert contract.address.startswith('ct')


def _sophia_contract_tx_call_online(node_cli, account):

    contract = node_cli.Contract(test_sophia_contract)
    tx = contract.tx_create(account, gas=100000)
    print("contract: ", contract.address)
    print("tx contract: ", tx)

    _, result = contract.tx_call(account, 'main', '42', gas=500000)
    assert result is not None
    assert result.return_type == 'ok'
    print("return", result.return_value)
    print("raw", hashing.decode(result.return_value))
    # assert result.return_value.lower() == hashing.encode("cb", f'{hex(42)[2:].zfill(64).lower()}')

    val, remote_type = contract.decode_data(result.return_value, 'int')
    assert val == 42
    assert remote_type == 'word'


def test_sophia_contract_tx_create_native(chain_fixture):
    # save settings and go online
    _sophia_contract_tx_create_online(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)


def test_sophia_contract_tx_call_native(chain_fixture):
    # save settings and go online
    _sophia_contract_tx_call_online(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)
    # restore settings


@pytest.mark.skip('Debug transaction disabled')
def test_sophia_contract_tx_create_debug(chain_fixture):
    # TODO: create a debug impl and test
    # save settings and go online
    _sophia_contract_tx_create_online(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)
    # restore settings


@pytest.mark.skip('Debug transaction disabled')
def test_sophia_contract_tx_call_debug(chain_fixture):
    # TODO: create a debug impl and test
    # save settings and go online
    _sophia_contract_tx_call_online(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)
    # restore settings

# test contracts


def test_sophia_contract_compile(compiler_fixture):

    tests = [
        {
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  function init(value : int) : state = { data = value }\n  function get() : int = state.data\n  function set(value : int) = put(state{data = value})",
            "bytecode": "cb_+QYYRgKgf6Gy7VnRXycsYSiFGAUHhMs+Oeg+RJvmPzCSAnxk8LT5BKX5AUmgOoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugeDc2V0uMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoP//////////////////////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////jJoEnsSQdsAgNxJqQzA+rc5DsuLDKUV7ETxQp+ItyJgJS3g2dldLhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA///////////////////////////////////////////uEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+QKLoOIjHWzfyTkW3kyzqYV79lz0D8JW9KFJiz9+fJgMGZNEhGluaXS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACg//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALkBoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQFEYgAAj2IAAMKRgICAUX9J7EkHbAIDcSakMwPq3OQ7LiwylFexE8UKfiLciYCUtxRiAAE5V1CAgFF/4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0QUYgAA0VdQgFF/OoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugcUYgABG1dQYAEZUQBbYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUpBZYABRWVJgAFJgAPNbYACAUmAA81tgAFFRkFZbYCABUVGQUIOSUICRUFCAWZCBUllgIAGQgVJgIJADYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUoFSkFCQVltgIAFRUVlQgJFQUGAAUYFZkIFSkFBgAFJZkFCQVltQUFlQUGIAAMpWhTIuMS4w4SWVhA==",
            "match": True
        }
    ]

    compiler = compiler_fixture.COMPILER
    for t in tests:
        result = compiler.compile(t.get('sourcecode'))
        print(result)
        assert (t.get("match") and result.bytecode == t.get("bytecode"))


@pytest.mark.skip("static call are disabled since 1.0.0")
def test_sophia_contract_call(chain_fixture):
    contract = chain_fixture.NODE_CLI.Contract(test_sophia_contract)
    result = contract.call('main', '1')
    assert result is not None
    assert result.out


def test_sophia_encode_calldata(compiler_fixture):
    tests = [
        {
            "function": "set",
            "arguments":  [42],
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACA6hZQte0c6B/XQTuHZwWpc6rFreRzqkolhGkTD+eW6BwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACoA4Uun",
            "match": True
        },
        {
            "function": "init",
            "arguments":  [42],
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDiIx1s38k5Ft5Ms6mFe/Zc9A/CVvShSYs/fnyYDBmTRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACo7j+li",
            "match": True
        },
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        result = compiler.encode_calldata(test_sophia_contract, t.get('function'), t.get('arguments'))
        assert (t.get("match") and result.calldata == t.get("calldata"))


def test_sophia_broken_contract_compile(chain_fixture):
    with raises(ContractError):
        contract = chain_fixture.NODE_CLI.Contract(broken_contract)
        print(contract.source_code)


def test_sophia_broken_contract_call(chain_fixture):
    with raises(ContractError):
        contract = chain_fixture.NODE_CLI.Contract(broken_contract)
        result = contract.call('IdentityBroken.main', '1')
        print(result)


def test_sophia_broken_encode_calldata(chain_fixture):
    with raises(ContractError):
        contract = chain_fixture.NODE_CLI.Contract(broken_contract)
        result = contract.encode_calldata('IdentityBroken.main', '1')
        print(result)

#
# EVM
#


def test_evm_contract_compile(chain_fixture):
    contract = chain_fixture.NODE_CLI.Contract(test_sophia_contract, abi=Contract.EVM)
    print(contract)
    assert contract.bytecode is not None
    assert utils.is_valid_hash(contract.bytecode, prefix='cb')

# TODO This call fails with an out of gas exception


@pytest.mark.skip('This call fails with an out of gas exception')
def test_evm_contract_call(chain_fixture):
    contract = chain_fixture.NODE_CLI.Contract(test_sophia_contract, abi=Contract.EVM)
    result = contract.call('main', '1')
    assert result is not None
    assert result.out


def test_evm_encode_calldata(chain_fixture):
    contract = chain_fixture.NODE_CLI.Contract(test_sophia_contract, abi=Contract.EVM)
    result = contract.encode_calldata('main', '1')
    assert result is not None
    assert result == hashing.encode('cb', 'main1')


def test_evm_broken_contract_compile(chain_fixture):
    with raises(ContractError):
        contract = chain_fixture.NODE_CLI.Contract(broken_contract, abi=Contract.EVM)
        print(contract.source_code)


def test_evm_broken_contract_call(chain_fixture):
    with raises(ContractError):
        contract = chain_fixture.NODE_CLI.Contract(broken_contract, abi=Contract.EVM)
        result = contract.call('IdentityBroken.main', '1')
        print(result)


def test_evm_broken_encode_calldata(chain_fixture):
    with raises(ContractError):
        contract = chain_fixture.NODE_CLI.Contract(broken_contract, abi=Contract.EVM)
        # with raises(AException):
        result = contract.encode_calldata('IdentityBroken.main', '1')
        print(result)
