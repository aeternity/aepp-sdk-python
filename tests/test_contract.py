import pytest
from pytest import raises

from aeternity.contract import ContractError, Contract
from tests import ACCOUNT, EPOCH_CLI
from aeternity import hashing, utils

aer_identity_contract = '''
contract Identity =
  type state = ()
  function main(x : int) = x
'''

broken_contract = '''
contract Identity =
  BROKEN state = ()
  function main(x : int) = x
'''

#
# SOPHIA
#


def _sophia_contract_tx_create_online():
    # runt tests
    contract = EPOCH_CLI.Contract(aer_identity_contract)
    contract.tx_create(ACCOUNT, gas=100000, fee=150000)
    assert contract.address is not None
    assert len(contract.address) > 0
    assert contract.address.startswith('ct')


def _sophia_contract_tx_call_online():

    contract = EPOCH_CLI.Contract(aer_identity_contract)
    tx = contract.tx_create(ACCOUNT, gas=100000, fee=150000)
    print("contract: ", contract.address)
    print("tx contract: ", tx)

    _, _, _, _, result = contract.tx_call(ACCOUNT, 'main', '42', gas=500000, fee=1000000)
    assert result is not None
    assert result.return_type == 'ok'
    print("return", result.return_value)
    print("raw", hashing.decode(result.return_value))
    # assert result.return_value.lower() == hashing.encode("cb", f'{hex(42)[2:].zfill(64).lower()}')

    val, remote_type = contract.decode_data(result.return_value, 'int')
    assert val == 42
    assert remote_type == 'word'


def test_sophia_contract_tx_create_native():
    # save settings and go online
    original = EPOCH_CLI.set_native(False)
    _sophia_contract_tx_create_online()
    # restore settings
    EPOCH_CLI.set_native(original)


def test_sophia_contract_tx_call_native():
    # save settings and go online
    original = EPOCH_CLI.set_native(False)
    _sophia_contract_tx_call_online()
    # restore settings
    EPOCH_CLI.set_native(original)


def test_sophia_contract_tx_create_debug():
    # save settings and go online
    original = EPOCH_CLI.set_native(False)
    _sophia_contract_tx_create_online()
    # restore settings
    EPOCH_CLI.set_native(original)


def test_sophia_contract_tx_call_debug():
    # save settings and go online
    original = EPOCH_CLI.set_native(False)
    _sophia_contract_tx_call_online()
    # restore settings
    EPOCH_CLI.set_native(original)

# test contracts


def test_sophia_contract_compile():
    contract = EPOCH_CLI.Contract(aer_identity_contract)
    assert contract is not None
    utils.is_valid_hash(contract.bytecode, prefix='cb')


@pytest.mark.skip("static call are disabled since 1.0.0")
def test_sophia_contract_call():
    contract = EPOCH_CLI.Contract(aer_identity_contract)
    result = contract.call('main', '1')
    assert result is not None
    assert result.out


def test_sophia_encode_calldata():
    contract = EPOCH_CLI.Contract(aer_identity_contract)
    result = contract.encode_calldata('main', '1')
    assert result is not None
    assert utils.is_valid_hash(result, prefix='cb')


def test_sophia_broken_contract_compile():
    with raises(ContractError):
        contract = EPOCH_CLI.Contract(broken_contract)
        print(contract.source_code)


def test_sophia_broken_contract_call():
    with raises(ContractError):
        contract = EPOCH_CLI.Contract(broken_contract)
        result = contract.call('IdentityBroken.main', '1')
        print(result)


def test_sophia_broken_encode_calldata():
    with raises(ContractError):
        contract = EPOCH_CLI.Contract(broken_contract)
        result = contract.encode_calldata('IdentityBroken.main', '1')
        print(result)

#
# EVM
#


def test_evm_contract_compile():
    contract = EPOCH_CLI.Contract(aer_identity_contract, abi=Contract.EVM)
    print(contract)
    assert contract.bytecode is not None
    assert utils.is_valid_hash(contract.bytecode, prefix='cb')

# TODO This call fails with an out of gas exception


@pytest.mark.skip('This call fails with an out of gas exception')
def test_evm_contract_call():
    contract = EPOCH_CLI.Contract(aer_identity_contract, abi=Contract.EVM)
    result = contract.call('main', '1')
    assert result is not None
    assert result.out


def test_evm_encode_calldata():
    contract = EPOCH_CLI.Contract(aer_identity_contract, abi=Contract.EVM)
    result = contract.encode_calldata('main', '1')
    assert result is not None
    assert result == hashing.encode('cb', 'main1')


def test_evm_broken_contract_compile():
    with raises(ContractError):
        contract = EPOCH_CLI.Contract(broken_contract, abi=Contract.EVM)
        print(contract.source_code)


def test_evm_broken_contract_call():
    with raises(ContractError):
        contract = EPOCH_CLI.Contract(broken_contract, abi=Contract.EVM)
        result = contract.call('IdentityBroken.main', '1')
        print(result)


def test_evm_broken_encode_calldata():
    with raises(ContractError):
        contract = EPOCH_CLI.Contract(broken_contract, abi=Contract.EVM)
        # with raises(AException):
        result = contract.encode_calldata('IdentityBroken.main', '1')
        print(result)
