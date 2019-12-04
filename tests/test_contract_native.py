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
    contract_native.deploy("abcd", 12, "A")
    assert(contract_native.address is not None)

    _, call_result = contract_native.intFn(12)
    assert(call_result == 12)

    _, call_result = contract_native.stringFn("test_call")
    assert(call_result == 'test_call')

    _, call_result = contract_native.addressFn(chain_fixture.ALICE.get_address())
    assert(call_result == chain_fixture.ALICE.get_address())

    _, call_result = contract_native.boolFn(False)
    assert(call_result == False)

    _, call_result = contract_native.tupleFn(["test", 1])
    assert(call_result == ["test", 1])

    _, call_result = contract_native.listFn([1,2,3,4,5])
    assert(call_result == [1,2,3,4,5])

    _, call_result = contract_native.mapFn({"ak_2a1j2Mk9YSmC1gioUq4PWRm3bsv887MbuRVwyv4KaUGoR1eiKi": ["test", 12]})
    assert(call_result == {'ak_2a1j2Mk9YSmC1gioUq4PWRm3bsv887MbuRVwyv4KaUGoR1eiKi': ['test', 12]})

    _, call_result = contract_native.intOption(12)
    assert(call_result == 12)

    _, call_result = contract_native.setRecord({"value": "test1", "key": 12, "testOption": "test2"})
    assert(call_result == [])

    _, call_result = contract_native.getRecord()
    assert(call_result == {'key': 12, 'testOption': 'test2', 'value': 'test1'})

    _, call_result = contract_native.retrieve()
    assert(call_result == ['test1', 12])

    _, call_result = contract_native.datTypeFn({"Year": []})
    assert(call_result == 'Year')

    try:
      call_info = contract_native.intOption(12, 13)
      raise ValueError("Method call should fail")
    except Exception as e:
      expected_error_message = "Invalid number of arguments. Expected 1, Provided 2"
      assert(str(e) == expected_error_message)


def test_contract_native_without_init(compiler_fixture, chain_fixture):
    identity_contract = "contract Identity =\n  entrypoint main(x : int) = x"
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler, account=account)
    contract_native.deploy()
    assert(contract_native.address is not None)
    _, call_result = contract_native.main(12)
    assert(call_result == 12)

def test_contract_native_without_default_account(compiler_fixture, chain_fixture):
    identity_contract = "contract Identity =\n  entrypoint main(x : int) = x"
    compiler = compiler_fixture.COMPILER
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler)
    contract_native.deploy(account=chain_fixture.ALICE)
    assert(contract_native.address is not None)
    call_info, call_result = contract_native.main(12, account=chain_fixture.BOB)
    assert(call_result == 12)
    try:
      _, call_result = contract_native.main(12)
      raise ValueError("Method call should fail")
    except Exception as e:
      assert(str(e) == "Please provide an account to sign contract call transactions. You can set a default account using 'set_account' method")

def test_contract_native_default_account_overriding(compiler_fixture, chain_fixture):
    identity_contract = "contract Identity =\n  entrypoint main(x : int) = x"
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler, account=account)
    contract_native.deploy()
    assert(contract_native.address is not None)
    call_info, _ = contract_native.main(12)
    assert(call_info.caller_id == chain_fixture.ALICE.get_address())

    call_info, _ = contract_native.main(12, account=chain_fixture.BOB)
    assert(call_info.caller_id == chain_fixture.BOB.get_address())

    contract_native.set_account(chain_fixture.BOB)
    call_info, _ = contract_native.main(12)
    assert(call_info.caller_id == chain_fixture.BOB.get_address())

def test_contract_native_without_dry_run(compiler_fixture, chain_fixture):
    identity_contract = "contract Identity =\n  entrypoint main(x : int) = x"
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler, account=account)
    contract_native.deploy()
    assert(contract_native.address is not None)

    call_info, call_result = contract_native.main(12)
    assert(call_result == 12 and not hasattr(call_info, 'tx_hash'))

    call_info, call_result = contract_native.main(12, use_dry_run=False)
    assert(call_result == 12 and hasattr(call_info, 'tx_hash'))

def test_contract_native_verify_contract_id(compiler_fixture, chain_fixture):
    identity_contract = "contract Identity =\n  entrypoint main(x : int) = x"
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler, account=account)
    contract_native.deploy()
    contract_native.at(contract_native.address)

    INVALID_ADDRESS = 'ct_M9yohHgcLjhpp1Z8SaA1UTmRMQzR4FWjJHajGga8KBoZTEPwC'

    try:
      contract_native.at(INVALID_ADDRESS)
    except Exception as e:
      assert str(e) == 'Contract not deployed'