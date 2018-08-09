import pytest
from pytest import raises

from aeternity.contract import Contract, ContractError
from aeternity.tests import KEYPAIR

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


def test_sophia_contract_tx_create():
    contract = Contract(aer_identity_contract)
    contract.tx_create(KEYPAIR, gas=10000)
    assert contract.address is not None
    assert len(contract.address) > 0
    assert contract.address.startswith('ct')


def test_sophia_contract_tx_call():
    contract = Contract(aer_identity_contract)
    tx = contract.tx_create_wait(KEYPAIR, gas=10000)
    print("contract: ", contract.address)
    print("tx contract: ", tx)

    result = contract.tx_call(KEYPAIR, 'main', '42')
    assert result is not None
    assert result.return_type == 'ok'
    assert result.return_value.lower() == f'0x{hex(42)[2:].zfill(64).lower()}'

    val, remote_type = contract.decode_data(result.return_value, 'int')
    assert val == 42
    assert remote_type == 'word'


# test contracts


def test_sophia_contract_compile():
    contract = Contract(aer_identity_contract)
    assert contract is not None
    assert contract.bytecode.startswith('0x')


def test_sophia_contract_call():
    contract = Contract(aer_identity_contract)
    result = contract.call('main', '1')
    assert result is not None
    assert result.out


def test_sophia_encode_calldata():
    contract = Contract(aer_identity_contract)
    result = contract.encode_calldata('main', '1')
    assert result is not None
    assert result.startswith('0x')


def test_sophia_broken_contract_compile():
    with raises(ContractError):
        contract = Contract(broken_contract)
        print(contract.source_code)


def test_sophia_broken_contract_call():
    with raises(ContractError):
        contract = Contract(broken_contract)
        result = contract.call('IdentityBroken.main', '1')
        print(result)


def test_sophia_broken_encode_calldata():
    with raises(ContractError):
        contract = Contract(broken_contract)
        result = contract.encode_calldata('IdentityBroken.main', '1')
        print(result)

#
# EVM
#


def test_evm_contract_compile():
    contract = Contract(aer_identity_contract, abi=Contract.EVM)
    print(contract)
    assert contract.bytecode is not None
    assert contract.bytecode.startswith('0x')

# TODO This call fails with an out of gas exception


@pytest.mark.skip('This call fails with an out of gas exception')
def test_evm_contract_call():
    contract = Contract(aer_identity_contract, abi=Contract.EVM)
    result = contract.call('main', '1')
    assert result is not None
    assert result.out


def test_evm_encode_calldata():
    contract = Contract(aer_identity_contract, abi=Contract.EVM)
    result = contract.encode_calldata('main', '1')
    assert result is not None
    assert result == 'main1'


def test_evm_broken_contract_compile():
    with raises(ContractError):
        contract = Contract(broken_contract, abi=Contract.EVM)
        print(contract.source_code)


def test_evm_broken_contract_call():
    with raises(ContractError):
        contract = Contract(broken_contract, abi=Contract.EVM)
        result = contract.call('IdentityBroken.main', '1')
        print(result)


def test_evm_broken_encode_calldata():
    with raises(ContractError):
        contract = Contract(broken_contract, abi=Contract.EVM)
        # with raises(AException):
        result = contract.encode_calldata('IdentityBroken.main', '1')
        print(result)
