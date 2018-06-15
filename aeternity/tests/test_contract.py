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
    contract = Contract(aer_identity_contract, Contract.SOPHIA)
    address, tx = contract.tx_create(KEYPAIR, gas=1000)
    assert address is not None
    assert len(address) > 0


def test_sophia_contract_tx_call():
    contract = Contract(aer_identity_contract, Contract.SOPHIA)
    address, tx = contract.tx_create_wait(KEYPAIR, gas=1000)
    print("contract: ", address)
    print("tx contract: ", tx)

    result = contract.tx_call(address, KEYPAIR, 'main', '42')
    assert result is not None
    assert result.return_type == 'ok'
    assert result.return_value.lower() == f'0x{hex(42)[2:].zfill(64).lower()}'

# test contracts


def test_sophia_contract_compile():
    contract = Contract(aer_identity_contract, Contract.SOPHIA)
    result = contract.compile('')
    assert result is not None
    assert result.startswith('0x')


def test_sophia_contract_call():
    contract = Contract(aer_identity_contract, Contract.SOPHIA)
    result = contract.call('main', '1')
    assert result is not None
    assert result.out


def test_sophia_encode_calldata():
    contract = Contract(aer_identity_contract, Contract.SOPHIA)
    result = contract.encode_calldata('main', '1')
    assert result is not None
    assert result == 'main1'


def test_sophia_broken_contract_compile():
    contract = Contract(broken_contract, Contract.SOPHIA)
    with raises(ContractError):
        result = contract.compile('')
        print(result)


def test_sophia_broken_contract_call():
    contract = Contract(broken_contract, Contract.SOPHIA)
    with raises(ContractError):
        result = contract.call('IdentityBroken.main', '1')
        print(result)

# TODO For some reason encoding the calldata for the broken contract does not raise an exception


@pytest.mark.skip('For some reason encoding the calldata for the broken contract '
                  'does not raise an exception')
def test_sophia_broken_encode_calldata():
    contract = Contract(broken_contract, Contract.SOPHIA)
    with raises(ContractError):
        result = contract.encode_calldata('IdentityBroken.main', '1')
        print(result)

#
# EVM
#


def test_evm_contract_compile():
    contract = Contract(aer_identity_contract, Contract.EVM)
    result = contract.compile()
    print(result)
    assert result is not None
    assert result.startswith('0x')

# TODO This call fails with an out of gas exception


@pytest.mark.skip('This call fails with an out of gas exception')
def test_evm_contract_call():
    contract = Contract(aer_identity_contract, Contract.EVM)
    result = contract.call('main', '1')
    assert result is not None
    assert result.out


def test_evm_encode_calldata():
    contract = Contract(aer_identity_contract, Contract.EVM)
    result = contract.encode_calldata('main', '1')
    assert result is not None
    assert result == 'main1'


def test_evm_broken_contract_compile():
    contract = Contract(broken_contract, Contract.EVM)
    with raises(ContractError):
        result = contract.compile('')
        print(result)


def test_evm_broken_contract_call():
    contract = Contract(broken_contract, Contract.EVM)
    with raises(ContractError):
        result = contract.call('IdentityBroken.main', '1')
        print(result)


def test_evm_broken_encode_calldata():
    contract = Contract(broken_contract, Contract.EVM)
    # with raises(AException):
    result = contract.encode_calldata('IdentityBroken.main', '1')
    print(result)
