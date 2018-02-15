from aeternity import EpochClient
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

def test_contract_compile():
    contract = Contract(example_contract, Contract.RING)
    result = contract.compile('')
    assert result is not None
    assert result.startswith('0x')

def test_contract_call():
    contract = Contract(example_contract, Contract.RING)
    result = contract.call('Identity.main', '1')
    assert result is not None
    assert result.get('out')

def test_encode_calldata():
    contract = Contract(example_contract, Contract.RING)
    result = contract.encode_calldata('Identity.main', '1')
    assert result is not None
    assert result == 'Identity.main1'
