import pytest
import namedtupled
from aeternity.contract_native import SophiaTransformation


contract = """contract StateContract =
  type number = int
  record state = { value: string, key: number, testOption: option(string) }
  record yesEr = { t: number}
  
  datatype dateUnit = Year | Month | Day

  entrypoint init(value: string, key: int, testOption: option(string)) : state = { value = value, key = key, testOption = testOption }
  entrypoint retrieve() : string*int = (state.value, state.key)

  entrypoint intFn(a: int) : int = a
  payable entrypoint stringFn(a: string) : string = a
  entrypoint boolFn(a: bool) : bool = a
  entrypoint addressFn(a: address) : address = a
  entrypoint contractAddress (ct: address) : address = ct
  entrypoint accountAddress (ak: address) : address = ak

  entrypoint tupleFn (a: string*int) : string*int = a
  entrypoint tupleInTupleFn (a: (string*string)*int) : (string*string)*int = a
  entrypoint tupleWithList (a: list(int)*int) : list(int)*int = a
  
  entrypoint listFn(a: list(int)) : list(int) = a
  entrypoint listInListFn(a: list(list(int))) : list(list(int)) = a
  
  entrypoint mapFn(a: map(address, string*int)) : map(address, string*int) = a
  entrypoint mapOptionFn(a: map(address, string*option(int))) : map(address, string*option(int)) = a
  
  entrypoint getRecord() : state = state
  stateful entrypoint setRecord(s: state) = put(s)
  
  entrypoint intOption(s: option(int)) : option(int) = s
  entrypoint listOption(s: option(list(int*string))) : option(list(int*string)) = s
  
  entrypoint testFn(a: list(int), b: bool) : list(int)*bool = (a, b)
  
  entrypoint hashFn(s: hash): hash = s
  entrypoint signatureFn(s: signature): signature = s
  entrypoint bytesFn(s: bytes(32)): bytes(32) = s
  entrypoint datTypeFn(s: dateUnit): dateUnit = s"""

def test_type_conversion_to_sophia(compiler_fixture, testdata_fixture):
    tests = [
        {
            "method": 2, #intFn
            "argument": 0,
            "values": 12,
            "result": "12",
            "match": True
        },
        {
            "method": 2,  # intFn
            "argument": 0,
            "values": 12,
            "result": 12,
            "match": False
        },
        {
            "method": 3,  # stringFn
            "argument": 0,
            "values": "A",
            "result": '/"A/"',
            "match": True
        },
        {
            "method": 3,  # stringFn
            "argument": 0,
            "values": "A",
            "result": "12",
            "match": False
        }
    ]

    compiler = compiler_fixture.COMPILER
    bytecode = compiler.compile(contract)
    contract_aci = compiler.aci(contract)
    transformer = SophiaTransformation()
    for t in tests:
         typeDef = namedtupled.reduce(contract_aci.encoded_aci.contract.functions[t.get('method')].arguments[t.get('argument')].type)
         transformed = transformer.convert_to_sophia(t.get('values'), typeDef)
         print(transformed)
         assert(t.get('match') == (transformed == t.get('result')))
