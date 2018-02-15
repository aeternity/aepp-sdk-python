from aeternity.contract import Contract

# see: /epoch/apps/aering/test/contracts/identity.aer
example_contract = '''
contract type Identity = {
  type state;

  let main: int => int;
};

contract Identity = {
  let main(x:int) = {
    x;
  };
};
'''

#
# RING
#

def test_ring_contract_compile():
    contract = Contract(example_contract, Contract.RING)
    result = contract.compile('')
    assert result is not None
    assert result.startswith('0x')

def test_ring_contract_call():
    contract = Contract(example_contract, Contract.RING)
    result = contract.call('Identity.main', '1')
    assert result is not None
    assert result.get('out')

def test_ring_encode_calldata():
    contract = Contract(example_contract, Contract.RING)
    result = contract.encode_calldata('Identity.main', '1')
    assert result is not None
    assert result == 'Identity.main1'

#
# EVM
#

def test_evm_contract_compile():
    contract = Contract(example_contract, Contract.EVM)
    result = contract.compile('')
    assert result is not None
    assert result.startswith('0x')

def test_evm_contract_call():
    contract = Contract(example_contract, Contract.EVM)
    result = contract.call('Identity.main', '1')
    assert result is not None
    assert result.get('out')

def test_evm_encode_calldata():
    contract = Contract(example_contract, Contract.EVM)
    result = contract.encode_calldata('Identity.main', '1')
    assert result is not None
    assert result == 'Identity.main1'
