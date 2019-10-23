from aeternity.contract_native import ContractNative


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


def test_contract_native(compiler_fixture, chain_fixture):
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=contract, compiler=compiler, account=account)
    contract_native.deploy("init", '\"abcd\"', "12", 'Some(\"A\")')
    assert(contract_native.address is not None)
    call_info = contract_native.intFn(12)
    assert(call_info.return_type == 'ok')
