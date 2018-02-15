from aeternity import EpochClient
from aeternity.contract import Contract

client = EpochClient()

# see: /epoch/apps/aering/test/contracts/05_greeter.aer
example_contract = '''
contract type Counter = {
  type state;
  let init : unit => state;
  let get  : unit => int;
  let tick : unit => unit;
};

contract Counter = {

  type state = int;

  let init() = 0;

  let get() = {
    let s = state();
    (s, s)
  };

  let tick() = {
    let s = state();
    ((), s + 1)
  };
};


'''

def test_contract_compile():
    contract = Contract(client)
    result = contract.contract_compile(example_contract, '')
    assert result is not None
    print(result)
    assert result.get('bytecode')

def test_contract_call():
    contract = Contract(client)
    result = contract.call(example_contract, 'init', '0x9')
    assert result is not None
    assert result.get('out')

def test_encode_calldata():
    contract = Contract(client)
    result = contract.encode_calldata(example_contract, 'init', '1')
    assert result is not None
    assert result.startswith('0x')
