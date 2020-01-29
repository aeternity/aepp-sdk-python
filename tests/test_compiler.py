import pytest
from aeternity.contract_native import ContractNative

def test_sophia_contract_compile(compiler_fixture, testdata_fixture):
    tests = [
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  function get() : int = state.data\n  stateful function set(value : int) = put(state{data = value})\n"
        },
    ]

    compiler = compiler_fixture.COMPILER
    for t in tests:
        result = compiler.compile(t.get('sourcecode'))
        assert hasattr(result, 'bytecode') and result.bytecode.startswith('cb_')


def test_sophia_encode_calldata(compiler_fixture):
    tests = [
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  function get() : int = state.data\n  stateful function set(value : int) = put(state{data = value})\n",
            "function": "set",
            "arguments":  [42],
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  function get() : int = state.data\n  stateful function set(value : int) = put(state{data = value})\n",
            "function": "init",
            "arguments":  [42],
        },
        {
            "sourcecode": "contract Identity =\n  entrypoint main(z : int) = z",
            "function": "init",
            "arguments":  [],
        },
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        result = compiler.encode_calldata(t.get("sourcecode"), t.get('function'), *t.get('arguments'))
        assert hasattr(result, 'calldata') and result.calldata.startswith("cb_")


def test_sophia_decode_data(compiler_fixture):
    tests = [
        {
            "sophia_type": "int",
            "encoded_data": "cb_KxHoxF62G1Sy3bqn",
            "expected.type": "word",
            "expected.value": 42,
            "match": True
        }
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        result = compiler.decode_data(t.get("sophia_type"), t.get('encoded_data'))
        assert (t.get("match") and (
            result.data.type == t.get("expected.type") and
            result.data.value == t.get("expected.value")
        ))


def test_sophia_decode_calldata_bytecode(compiler_fixture):
    tests = [
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  entrypoint get() : int = state.data\n  stateful entrypoint set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+JFGA6DcSHcAbyhLqfbIDJRe1S7ZJLCZQJBUuvMmCLK5OirpHsC4YLg8/i+GW9kANwAHKCwAggD+RNZEHwA3AQc3AAwBACcMAhoCggEDP/7oxF62ADcBBzcADAEAJwwCGgKCAQM/ni8DES+GW9kNZ2V0EUTWRB8RaW5pdBHoxF62DXNldIIvAIk0LjAuMC1yYzUAFlcOUg==",
            "match": True,
            "target_protocol": 4,
            "calldata": "cb_KxHoxF62G1Sy3bqn",
            "function": "set",
            "arguments":  [42],
        },
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
            "bytecode": "cb_+GpGA6Abk28ISckRxfWDHCo6FYfNzlAYCRW6TBDvQZ2BYQUmH8C4OZ7+RNZEHwA3ADcAGg6CPwEDP/64F37sADcBBwcBAQCWLwIRRNZEHxFpbml0EbgXfuwRbWFpboIvAIk0LjAuMC1yYzUAfpEWYw==",
            "match": True,
            "target_protocol": 4,
            "calldata": "cb_KxG4F37sG1Q/+F7e",
            "function": "main",
            "arguments":  [42],
        }
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        if compiler.target_protocol == t.get("target_protocol"):
            result = compiler.decode_calldata_with_bytecode(t.get("bytecode"), t.get('calldata'))
            print("RESULT", result)
            assert (t.get("match") and (
                result.function == t.get("function") and
                result.arguments[0].value == t.get("arguments")[0]
            ))

def test_sophia_validate_bytecode(compiler_fixture, chain_fixture):
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    node_client = chain_fixture.NODE_CLI

    sourcecode = """contract SimpleStorage =
      record state = { data : int }
      entrypoint init(value : int) : state = { data = value }
      entrypoint get() : int = state.data
      stateful entrypoint set(value : int) = put(state{data = value})"""

    contract_native = ContractNative(client=node_client, source=sourcecode, compiler=compiler, account=account)
    contract_native.deploy(12)

    chain_bytecode = node_client.get_contract_code(pubkey=contract_native.address).bytecode
    result = compiler.validate_bytecode(sourcecode, chain_bytecode)

    assert result == {}

    sourcecode_identity = """contract Identity =
    entrypoint main(x : int) = x
    entrypoint mainString(x : string) = x"""

    try:
        result = compiler.validate_bytecode(sourcecode_identity, chain_bytecode)
        raise RuntimeError("Method call should fail")
    except Exception as e:
      assert str(e) == 'Invalid contract'

@pytest.mark.skip("to be verified")
def test_sophia_decode_calldata_sourcecode(compiler_fixture):
    tests = [
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  entrypoint get() : int = state.data\n  stateful entrypoint set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+JFGA6DcSHcAbyhLqfbIDJRe1S7ZJLCZQJBUuvMmCLK5OirpHsC4YLg8/i+GW9kANwAHKCwAggD+RNZEHwA3AQc3AAwBACcMAhoCggEDP/7oxF62ADcBBzcADAEAJwwCGgKCAQM/ni8DES+GW9kNZ2V0EUTWRB8RaW5pdBHoxF62DXNldIIvAIk0LjAuMC1yYzUAFlcOUg==",
            "match": True,
            "target_protocol": 4,
            "calldata": "cb_KxHoxF62G1Sy3bqn",
            "function": "set",
            "arguments":  [42],
        },
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
            "bytecode": "cb_+GpGA6Abk28ISckRxfWDHCo6FYfNzlAYCRW6TBDvQZ2BYQUmH8C4OZ7+RNZEHwA3ADcAGg6CPwEDP/64F37sADcBBwcBAQCWLwIRRNZEHxFpbml0EbgXfuwRbWFpboIvAIk0LjAuMC1yYzUAfpEWYw==",
            "match": True,
            "target_protocol": 4,
            "calldata": "cb_KxG4F37sG1Q/+F7e",
            "function": "main",
            "arguments":  [42],
        }
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        if compiler.target_protocol == t.get("target_protocol"):
            result = compiler.decode_calldata_with_sourcecode(t.get("sourcecode"), t.get('function'), t.get('calldata'))
            assert (t.get("match") and (
                result.function == t.get("function") and
                result.arguments[0].value == t.get("sophia_value")
            ))
