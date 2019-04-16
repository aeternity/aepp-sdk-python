import pytest


#
# SOPHIA
#


def _sophia_contract_tx_create_online(node_cli, account):
    tests = [
        {
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  function init(value : int) : state = " +
            "{ data = value }\n  function get() : int = state.data\n  function set(value : int) = put(state{data = value})",
            "bytecode": "cb_+QYYRgKgf6Gy7VnRXycsYSiFGAUHhMs+Oeg+RJvmPzCSAnxk8LT5BKX5AUmgOoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw" +
            "/nlugeDc2V0uMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoP///////////////////////////////////////" +
            "///AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////jJoEnsSQdsAgNxJqQzA+rc5DsuLDKUV7ETxQp+ItyJgJS3g" +
            "2dldLhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////////////////////" +
            "///////////////////////uEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+" +
            "QKLoOIjHWzfyTkW3kyzqYV79lz0D8JW9KFJiz9+fJgMGZNEhGluaXS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "ACg//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALkBoAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "YD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQFEYgAAj2IAAMKRgICAUX9J7" +
            "EkHbAIDcSakMwPq3OQ7LiwylFexE8UKfiLciYCUtxRiAAE5V1CAgFF/4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0QUYgAA0VdQgFF/O" +
            "oWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugcUYgABG1dQYAEZUQBbYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUpBZY" +
            "ABRWVJgAFJgAPNbYACAUmAA81tgAFFRkFZbYCABUVGQUIOSUICRUFCAWZCBUllgIAGQgVJgIJADYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQg" +
            "VJgIJADYAOBUoFSkFCQVltgIAFRUVlQgJFQUGAAUYFZkIFSkFBgAFJZkFCQVltQUFlQUGIAAMpWhTIuMS4w4SWVhA==""",
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDiIx1s38k5Ft5Ms6mFe/Zc9A/CVvShSYs/fnyYDBmTRAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACo7j+li"  # init(42)
        },
        {
            "sourcecode": "contract Identity =\n  type state = ()\n  function main(z : int) = z",
            "bytecode": "cb_+QP1RgKgpVq1Ib2r2ug+UktHvfWSQ8P35HJQHM6qikqBu1DwgtT5Avv5ASqgaPJnYzj/UIg5q6R3Se/6i+h+8oTyB/s9mZhwH" +
            "NU4h8WEbWFpbrjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKD//////////////////////////////////////" +
            "////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAA+QHLoLnJVvKLMUmp9Zh6pQXz2hsiCcxXOSNABiu2wb2fn5nqhGluaXS4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP//////////////////////////////////////////7kBQAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA///////////////////////////////////////////uMxiAABkYgAAhJGAgIBRf7nJVvKLMUmp9" +
            "Zh6pQXz2hsiCcxXOSNABiu2wb2fn5nqFGIAAMBXUIBRf2jyZ2M4/1CIOaukd0nv+ovofvKE8gf7PZmYcBzVOIfFFGIAAK9XUGABGVEAW2AAGVlgI" +
            "AGQgVJgIJADYAOBUpBZYABRWVJgAFJgAPNbYACAUmAA81tZWWAgAZCBUmAgkANgABlZYCABkIFSYCCQA2ADgVKBUpBWW2AgAVFRWVCAkVBQgJBQk" +
            "FZbUFCCkVBQYgAAjFaFMi4xLjBJtQib",
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACC5yVbyizFJqfWYeqUF89obIgnMVzkjQAYrtsG9n5+Z6gAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnHQYrA=="  # init()
        }

    ]
    for t in tests:
        contract = node_cli.Contract()
        contract.create(account, t.get("bytecode"), init_calldata=t.get("calldata"), gas=100000)
        deployed = node_cli.get_contract(pubkey=contract.address)
        assert deployed.active is True
        assert deployed.owner_id == account.get_address()


def _sophia_contract_tx_call_online(node_cli, account):
    tests = [
        {
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  function init(value : int) : state = " +
            "{ data = value }\n  function get() : int = state.data\n  function set(value : int) = put(state{data = value})",
            "bytecode": "cb_+QYYRgKgf6Gy7VnRXycsYSiFGAUHhMs+Oeg+RJvmPzCSAnxk8LT5BKX5AUmgOoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw" +
            "/nlugeDc2V0uMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoP///////////////////////////////////////" +
            "///AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////jJoEnsSQdsAgNxJqQzA+rc5DsuLDKUV7ETxQp+ItyJgJS3g" +
            "2dldLhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////////////////////" +
            "///////////////////////uEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+" +
            "QKLoOIjHWzfyTkW3kyzqYV79lz0D8JW9KFJiz9+fJgMGZNEhGluaXS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "ACg//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALkBoAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "YD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQFEYgAAj2IAAMKRgICAUX9J7" +
            "EkHbAIDcSakMwPq3OQ7LiwylFexE8UKfiLciYCUtxRiAAE5V1CAgFF/4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0QUYgAA0VdQgFF/O" +
            "oWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugcUYgABG1dQYAEZUQBbYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUpBZY" +
            "ABRWVJgAFJgAPNbYACAUmAA81tgAFFRkFZbYCABUVGQUIOSUICRUFCAWZCBUllgIAGQgVJgIJADYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQg" +
            "VJgIJADYAOBUoFSkFCQVltgIAFRUVlQgJFQUGAAUYFZkIFSkFBgAFJZkFCQVltQUFlQUGIAAMpWhTIuMS4w4SWVhA==""",
            "init.calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDiIx1s38k5Ft5Ms6mFe/Zc9A/CVvShSYs/fnyYDBmTRAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACo7j+li",  # init(42)
            "call.function": "set",
            "call.arguments": [24],
            "call.calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACA6hZQte0c6B/XQTuHZwWpc6rFreRzqkolhGkTD+eW6BwAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABhl+sL5",
            "return.value": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAArMtts"  # 0,
        },
        {
            "sourcecode": "contract Identity =\n  type state = ()\n  function main(z : int) = z",
            "bytecode": "cb_+QP1RgKgpVq1Ib2r2ug+UktHvfWSQ8P35HJQHM6qikqBu1DwgtT5Avv5ASqgaPJnYzj/UIg5q6R3Se/6i+h+8oTyB/s9mZhwH" +
            "NU4h8WEbWFpbrjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKD//////////////////////////////////////" +
            "////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAA+QHLoLnJVvKLMUmp9Zh6pQXz2hsiCcxXOSNABiu2wb2fn5nqhGluaXS4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP//////////////////////////////////////////7kBQAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA///////////////////////////////////////////uMxiAABkYgAAhJGAgIBRf7nJVvKLMUmp9" +
            "Zh6pQXz2hsiCcxXOSNABiu2wb2fn5nqFGIAAMBXUIBRf2jyZ2M4/1CIOaukd0nv+ovofvKE8gf7PZmYcBzVOIfFFGIAAK9XUGABGVEAW2AAGVlgI" +
            "AGQgVJgIJADYAOBUpBZYABRWVJgAFJgAPNbYACAUmAA81tZWWAgAZCBUmAgkANgABlZYCABkIFSYCCQA2ADgVKBUpBWW2AgAVFRWVCAkVBQgJBQk" +
            "FZbUFCCkVBQYgAAjFaFMi4xLjBJtQib",
            "init.calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACC5yVbyizFJqfWYeqUF89obIgnMVzkjQAYrtsG9n5+Z6gAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnHQYrA==",  # init()
            "call.function": "main",
            "call.arguments": [42],
            "call.calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBo8mdjOP9QiDmrpHdJ7/qL6H7yhPIH+z2ZmHAc1TiHxQAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACo7dbVl",
            "return.value": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACr8s/aY"  # 42

        }

    ]
    for t in tests:
        contract = node_cli.Contract()
        contract.create(account, t.get("bytecode"), init_calldata=t.get("init.calldata"), gas=100000)
        deployed = node_cli.get_contract(pubkey=contract.address)
        assert deployed.active is True
        assert deployed.owner_id == account.get_address()
        tx = contract.call(contract.address, account, t.get("call.function"), t.get("call.arguments"), t.get("call.calldata"),  gas=100000)
        # retrieve the call object
        call = contract.get_call_object(tx.hash)
        assert call.return_value == t.get("return.value")
        assert call.return_type == "ok"


def test_sophia_contract_tx_create_native(chain_fixture):
    # save settings and go online
    _sophia_contract_tx_create_online(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)


def test_sophia_contract_tx_call_native(chain_fixture):
    # save settings and go online
    _sophia_contract_tx_call_online(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)
    # restore settings


@pytest.mark.skip('Debug transaction disabled')
def test_sophia_contract_tx_create_debug(chain_fixture):
    # TODO: create a debug impl and test
    # save settings and go online
    _sophia_contract_tx_create_online(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)


@pytest.mark.skip('Debug transaction disabled')
def test_sophia_contract_tx_call_debug(chain_fixture):
    # TODO: create a debug impl and test
    # save settings and go online
    _sophia_contract_tx_call_online(chain_fixture.NODE_CLI, chain_fixture.ACCOUNT)

# test contracts


def test_sophia_contract_compile(compiler_fixture):
    tests = [
        {
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  function init(value : int) : state = " +
            "{ data = value }\n  function get() : int = state.data\n  function set(value : int) = put(state{data = value})",
            "bytecode": "cb_+QYYRgKgf6Gy7VnRXycsYSiFGAUHhMs+Oeg+RJvmPzCSAnxk8LT5BKX5AUmgOoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw" +
            "/nlugeDc2V0uMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoP///////////////////////////////////////" +
            "///AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////jJoEnsSQdsAgNxJqQzA+rc5DsuLDKUV7ETxQp+ItyJgJS3g" +
            "2dldLhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////////////////////" +
            "///////////////////////uEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+" +
            "QKLoOIjHWzfyTkW3kyzqYV79lz0D8JW9KFJiz9+fJgMGZNEhGluaXS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "ACg//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALkBoAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "YD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQFEYgAAj2IAAMKRgICAUX9J7" +
            "EkHbAIDcSakMwPq3OQ7LiwylFexE8UKfiLciYCUtxRiAAE5V1CAgFF/4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0QUYgAA0VdQgFF/O" +
            "oWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugcUYgABG1dQYAEZUQBbYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUpBZY" +
            "ABRWVJgAFJgAPNbYACAUmAA81tgAFFRkFZbYCABUVGQUIOSUICRUFCAWZCBUllgIAGQgVJgIJADYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQg" +
            "VJgIJADYAOBUoFSkFCQVltgIAFRUVlQgJFQUGAAUYFZkIFSkFBgAFJZkFCQVltQUFlQUGIAAMpWhTIuMS4w4SWVhA==""",
            "match": True
        }
    ]

    compiler = compiler_fixture.COMPILER
    for t in tests:
        result = compiler.compile(t.get('sourcecode'))
        print(result)
        assert (t.get("match") and result.bytecode == t.get("bytecode"))


def test_sophia_encode_calldata(compiler_fixture):
    tests = [
        {
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  function init(value : int) : state = " +
            "{ data = value }\n  function get() : int = state.data\n  function set(value : int) = put(state{data = value})",
            "function": "set",
            "arguments":  [42],
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACA6hZQte0c6B/XQTuHZwWpc6rFreRzqkolhGkTD+eW6BwAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACoA4Uun",
            "match": True
        },
        {
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  function init(value : int) : state = " +
            "{ data = value }\n  function get() : int = state.data\n  function set(value : int) = put(state{data = value})",
            "function": "init",
            "arguments":  [42],
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDiIx1s38k5Ft5Ms6mFe/Zc9A/CVvShSYs/fnyYDBmTRAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACo7j+li",
            "match": True
        },
        {
            "sourcecode": "contract Identity =\n  type state = ()\n  function main(z : int) = z",
            "function": "init",
            "arguments":  [],
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACC5yVbyizFJqfWYeqUF89obIgnMVzkjQAYrtsG9n5+Z6gAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAnHQYrA==",
            "match": True
        },
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        result = compiler.encode_calldata(t.get("sourcecode"), t.get('function'), t.get('arguments'))
        assert (t.get("match") and result.calldata == t.get("calldata"))


def test_sophia_decode_data(compiler_fixture):
    tests = [
        {
            "sophia_type": "int",
            "encoded_data": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACr8s/aY",
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
            "bytecode": "cb_+QYYRgKgf6Gy7VnRXycsYSiFGAUHhMs+Oeg+RJvmPzCSAnxk8LT5BKX5AUmgOoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw" +
            "/nlugeDc2V0uMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoP///////////////////////////////////////" +
            "///AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////jJoEnsSQdsAgNxJqQzA+rc5DsuLDKUV7ETxQp+ItyJgJS3g" +
            "2dldLhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////////////////////" +
            "///////////////////////uEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+" +
            "QKLoOIjHWzfyTkW3kyzqYV79lz0D8JW9KFJiz9+fJgMGZNEhGluaXS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "ACg//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALkBoAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "YD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQFEYgAAj2IAAMKRgICAUX9J7" +
            "EkHbAIDcSakMwPq3OQ7LiwylFexE8UKfiLciYCUtxRiAAE5V1CAgFF/4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0QUYgAA0VdQgFF/O" +
            "oWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugcUYgABG1dQYAEZUQBbYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUpBZY" +
            "ABRWVJgAFJgAPNbYACAUmAA81tgAFFRkFZbYCABUVGQUIOSUICRUFCAWZCBUllgIAGQgVJgIJADYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQg" +
            "VJgIJADYAOBUoFSkFCQVltgIAFRUVlQgJFQUGAAUYFZkIFSkFBgAFJZkFCQVltQUFlQUGIAAMpWhTIuMS4w4SWVhA==""",
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACA6hZQte0c6B/XQTuHZwWpc6rFreRzqkolhGkTD+eW6BwAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACoA4Uun",
            "function": "set",
            "arguments":  [42],

            "match": True
        },
        {
            "bytecode": "cb_+QYYRgKgf6Gy7VnRXycsYSiFGAUHhMs+Oeg+RJvmPzCSAnxk8LT5BKX5AUmgOoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw" +
            "/nlugeDc2V0uMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoP///////////////////////////////////////" +
            "///AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////jJoEnsSQdsAgNxJqQzA+rc5DsuLDKUV7ETxQp+ItyJgJS3g" +
            "2dldLhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA////////////////////" +
            "///////////////////////uEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+" +
            "QKLoOIjHWzfyTkW3kyzqYV79lz0D8JW9KFJiz9+fJgMGZNEhGluaXS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "ACg//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALkBoAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "AAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA" +
            "YD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQFEYgAAj2IAAMKRgICAUX9J7" +
            "EkHbAIDcSakMwPq3OQ7LiwylFexE8UKfiLciYCUtxRiAAE5V1CAgFF/4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0QUYgAA0VdQgFF/O" +
            "oWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugcUYgABG1dQYAEZUQBbYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUpBZY" +
            "ABRWVJgAFJgAPNbYACAUmAA81tgAFFRkFZbYCABUVGQUIOSUICRUFCAWZCBUllgIAGQgVJgIJADYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQg" +
            "VJgIJADYAOBUoFSkFCQVltgIAFRUVlQgJFQUGAAUYFZkIFSkFBgAFJZkFCQVltQUFlQUGIAAMpWhTIuMS4w4SWVhA==""",
            "function": "init",
            "arguments":  [42],
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDiIx1s38k5Ft5Ms6mFe/Zc9A/CVvShSYs/fnyYDBmTRAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACo7j+li",
            "match": True
        },
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        result = compiler.decode_calldata_with_bytecode(t.get("bytecode"), t.get('calldata'))
        assert (t.get("match") and (
            result.function == t.get("function") and
            result.arguments[0].value == t.get("arguments")[0]
        ))


def test_sophia_decode_calldata_sourcecode(compiler_fixture):
    tests = [
        {
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  function init(value : int) : state = " +
            "{ data = value }\n  function get() : int = state.data\n  function set(value : int) = put(state{data = value})",
            "function": "set",
            "sophia_value":  [52, 50],  # 42
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACA6hZQte0c6B/XQTuHZwWpc6rFreRzqkolhGkTD+eW6BwAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACoA4Uun",
            "match": True
        },
        {
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  function init(value : int) : state = " +
            "{ data = value }\n  function get() : int = state.data\n  function set(value : int) = put(state{data = value})",
            "function": "init",
            "sophia_value":  [52, 50],  # 42
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDiIx1s38k5Ft5Ms6mFe/Zc9A/CVvShSYs/fnyYDBmTRAAAAAAAAAAAA" +
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACo7j+li",
            "match": True
        },
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        result = compiler.decode_calldata_with_sourcecode(t.get("sourcecode"), t.get('function'), t.get('calldata'))
        assert (t.get("match") and (
            result.function == t.get("function") and
            result.arguments[0].value == t.get("sophia_value")
        ))


@pytest.mark.skip("static call are disabled since 1.0.0")
def test_sophia_contract_call(chain_fixture):
    contract = chain_fixture.NODE_CLI.Contract()
    result = contract.call('main', '1')
    assert result is not None
