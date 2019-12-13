from aeternity.contract_native import ContractNative


contract = """contract StateContract =
  type number = int
  record state = { value: string, key: number, testOption: option(string), testmap: map(string, string) }
  record yesEr = { t: number}
  datatype dateUnit = Year | Month | Day

  entrypoint init(value: string, key: int, testOption: option(string), testmap: map(string, string)) : state = { value = value, key = key, testOption = testOption, testmap = testmap }
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
  entrypoint datTypeFn(s: dateUnit): dateUnit = s
  entrypoint try_switch(name: string) = 
        switch(Map.lookup(name, state.testmap)) 
          Some(_name)  => _name 
          None         => abort("name not found")
  entrypoint cause_error_require() : unit =
        require(2 == 1, "require failed")
  entrypoint cause_error_abort() : unit =
        abort("triggered abort")
  payable stateful entrypoint spend_all() =
        Chain.spend(Call.origin, 1000000000000000000000000)"""


def test_contract_native_full(compiler_fixture, chain_fixture):
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=contract, compiler=compiler, account=account)
    contract_native.deploy("abcd", 12, "A", { "key": "value" })
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

    _, call_result = contract_native.setRecord({"value": "test1", "key": 12, "testOption": "test2", "testmap": { "key1": "value1" }})
    assert(call_result == [])

    _, call_result = contract_native.getRecord()
    assert(call_result == {'key': 12, 'testOption': 'test2', 'value': 'test1', "testmap": { "key1": "value1" }})

    _, call_result = contract_native.retrieve()
    assert(call_result == ['test1', 12])

    _, call_result = contract_native.datTypeFn({"Year": []})
    assert(call_result == 'Year')

    try:
      call_info = contract_native.intOption(12, 13)
      raise RuntimeError("Method call should fail")
    except Exception as e:
      expected_error_message = "Invalid number of arguments. Expected 1, Provided 2"
      assert(str(e) == expected_error_message)

    try:
      call_info, call_result =  contract_native.cause_error_require()
      raise RuntimeError("Method call should fail")
    except Exception as e:
      expected_error_message = "Error occurred while executing the contract method. Error Type: abort. Error Message: require failed"
      assert str(e) == expected_error_message
    
    try:
      call_info, call_result =  contract_native.cause_error_abort(use_dry_run=False)
      raise RuntimeError("Method call should fail")
    except Exception as e:
      expected_error_message = "Error occurred while executing the contract method. Error Type: abort. Error Message: triggered abort"
      assert str(e) == expected_error_message
    
    try:
      call_info, call_result = contract_native.spend_all()
      raise RuntimeError("Method call should fail")
    except Exception as e:
      expected_error_message = "Error occurred while executing the contract method. Error Type: error. Error Message: "
      assert str(e) == expected_error_message

    try:
      call_info, call_result = contract_native.try_switch('name1')
      raise RuntimeError("Method call should fail")
    except Exception as e:
      expected_error_message = "Error occurred while executing the contract method. Error Type: abort. Error Message: name not found"
      assert str(e) == expected_error_message
    

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

def test_contract_native_dry_run_without_account(compiler_fixture, chain_fixture):
    identity_contract = "contract Identity =\n  entrypoint main(x : int) = x"
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler, account=account)
    contract_native.deploy()
    assert(contract_native.address is not None)
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler, address=contract_native.address)
    call_info, call_result = contract_native.main(12)
    assert(call_result == 12 and not hasattr(call_info, 'tx_hash'))

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
      raise RuntimeError("Method call should fail")
    except Exception as e:
      assert str(e) == 'Contract not deployed'

    try:
      contract_native.at('ak_11111')
      raise RuntimeError("Method call should fail")
    except Exception as e:
      assert str(e) == 'Invalid contract address ak_11111'

def test_contract_native_init_errors(compiler_fixture, chain_fixture):
    identity_contract = "contract Identity =\n  entrypoint main(x : int) = x"
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    try:
      contract_native = ContractNative(source=identity_contract, compiler=compiler, account=account)
      raise RuntimeError("Method call should fail")
    except Exception as e:
      assert str(e) == 'Node client is not provided'

    try:
      contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, account=account)
      raise RuntimeError("Method call should fail")
    except Exception as e:
      assert str(e) == 'Compiler is not provided'

    try:
      contract_native = ContractNative(client=chain_fixture.NODE_CLI, compiler=compiler, account=account)
      raise RuntimeError("Method call should fail")
    except Exception as e:
      assert str(e) == 'contract source not provided'

    try:
      contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler, account='ak_11111111111111111111111111111111273Yts')
      raise RuntimeError("Method call should fail")
    except Exception as e:
      assert str(e) == 'Invalid account type. Use `class Account` for creating an account'

def test_contract_native_compiler_init_str(chain_fixture, compiler_fixture):
    identity_contract = "contract Identity =\n  entrypoint main(x : int) = x"
    account = chain_fixture.ALICE
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler_fixture.COMPILER.compiler_url, account=account)
    contract_native.deploy()
    assert(contract_native.address is not None)

def test_contract_native_compiler_set_account(chain_fixture, compiler_fixture):
    identity_contract = "contract Identity =\n  entrypoint main(x : int) = x"
    account = chain_fixture.ALICE
    try:
      contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler_fixture.COMPILER.compiler_url, account='ak_11111')
      raise RuntimeError("Method call should fail")
    except Exception as e:
      assert str(e) == 'Invalid account type. Use `class Account` for creating an account'

    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=identity_contract, compiler=compiler_fixture.COMPILER.compiler_url, account=account)

    try:
      contract_native.set_account(None)
      raise RuntimeError("Method call should fail")
    except Exception as e:
      assert str(e) == 'Account can not be of None type'

    try:
      contract_native.set_account('ak_111111')
      raise RuntimeError("Method call should fail")
    except Exception as e:
      assert str(e) == 'Invalid account type. Use `class Account` for creating an account'
