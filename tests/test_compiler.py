import pytest


def test_sophia_contract_compile(compiler_fixture, testdata_fixture):
    tests = [
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
            "bytecode": "cb_+QP1RgKgG5NvCEnJEcX1gxwqOhWHzc5QGAkVukwQ70GdgWEFJh/5Avv5ASqgaPJnYzj/UIg5q6R3Se/6i+h+8oTyB/s9mZhwHNU4h8WEbWFpbrjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+QHLoLnJVvKLMUmp9Zh6pQXz2hsiCcxXOSNABiu2wb2fn5nqhGluaXS4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP//////////////////////////////////////////7kBQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA///////////////////////////////////////////uMxiAABkYgAAhJGAgIBRf7nJVvKLMUmp9Zh6pQXz2hsiCcxXOSNABiu2wb2fn5nqFGIAAMBXUIBRf2jyZ2M4/1CIOaukd0nv+ovofvKE8gf7PZmYcBzVOIfFFGIAAK9XUGABGVEAW2AAGVlgIAGQgVJgIJADYAOBUpBZYABRWVJgAFJgAPNbYACAUmAA81tZWWAgAZCBUmAgkANgABlZYCABkIFSYCCQA2ADgVKBUpBWW2AgAVFRWVCAkVBQgJBQkFZbUFCCkVBQYgAAjFaFMy4yLjBaNtQ3",
            "match": True,
            "compiler.v.upto": 4
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  function get() : int = state.data\n  stateful function set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+QN+RgKgcPPaLbPhA5ZUYYI1viyMLIiudfF0RqUBtpvYh9wt5RL5Ao75Aoug4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0SEaW5pdLjAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQGgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgP//////////////////////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4wmIAADliAABskYCAUX/iIx1s38k5Ft5Ms6mFe/Zc9A/CVvShSYs/fnyYDBmTRBRiAACwV1BgARlRAFtgABlZYCABkIFSYCCQA2AAWZCBUoFSWWAgAZCBUmAgkANgA4FSkFlgAFFZUmAAUmAA81tgAIBSYADzW4BZkIFSWWAgAZCBUmAgkANgABlZYCABkIFSYCCQA2AAWZCBUoFSWWAgAZCBUmAgkANgA4FSgVKQUJBWW2AgAVFRg5JQgJFQUGIAAHRWhTMuMi4w4uI4dA==",
            "match": True,
            "compiler.v.upto": 4
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  entrypoint get() : int = state.data\n  stateful entrypoint set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+JFGA6DcSHcAbyhLqfbIDJRe1S7ZJLCZQJBUuvMmCLK5OirpHsC4YLg8/i+GW9kANwAHKCwAggD+RNZEHwA3AQc3AAwBACcMAhoCggEDP/7oxF62ADcBBzcADAEAJwwCGgKCAQM/ni8DES+GW9kNZ2V0EUTWRB8RaW5pdBHoxF62DXNldIIvAIk0LjAuMC1yYzUAFlcOUg==",
            "match": True,
            "compiler.v.upto": 5
        },
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
            "bytecode": "cb_+GpGA6Abk28ISckRxfWDHCo6FYfNzlAYCRW6TBDvQZ2BYQUmH8C4OZ7+RNZEHwA3ADcAGg6CPwEDP/64F37sADcBBwcBAQCWLwIRRNZEHxFpbml0EbgXfuwRbWFpboIvAIk0LjAuMC1yYzUAfpEWYw==",
            "match": True,
            "compiler.v.upto": 5
        }
    ]

    compiler = compiler_fixture.COMPILER
    for t in tests:
        if compiler.target_protocol < t.get("compiler.v.upto"):
            result = compiler.compile(t.get('sourcecode'))
            assert (t.get("match") and result.bytecode == t.get("bytecode"))


def test_sophia_encode_calldata(compiler_fixture):
    tests = [
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  function get() : int = state.data\n  stateful function set(value : int) = put(state{data = value})\n",
            "function": "set",
            "arguments":  [42],
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACA6hZQte0c6B/XQTuHZwWpc6rFreRzqkolhGkTD+eW6BwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACoA4Uun",
            "match": True,
            "compiler.v.upto": 4
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  function get() : int = state.data\n  stateful function set(value : int) = put(state{data = value})\n",
            "function": "init",
            "arguments":  [42],
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDiIx1s38k5Ft5Ms6mFe/Zc9A/CVvShSYs/fnyYDBmTRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACo7j+li",
            "match": True,
            "compiler.v.upto": 4
        },
        {
            "sourcecode": "contract Identity =\n  type state = ()\n  entrypoint main(z : int) = z",
            "function": "init",
            "arguments":  [],
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACC5yVbyizFJqfWYeqUF89obIgnMVzkjQAYrtsG9n5+Z6gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnHQYrA==",
            "match": True,
            "compiler.v.upto": 4
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  entrypoint get() : int = state.data\n  stateful entrypoint set(value : int) = put(state{data = value})\n",
            "calldata": "cb_KxFE1kQfG1TH2kjs",
            "function": "init",
            "arguments":  [42],
            "match": True,
            "compiler.v.upto": 5
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  entrypoint get() : int = state.data\n  stateful entrypoint set(value : int) = put(state{data = value})\n",
            "calldata": "cb_KxHoxF62G1Sy3bqn",
            "function": "set",
            "arguments":  [42],
            "match": True,
            "compiler.v.upto": 5
        },
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
            "calldata": "cb_KxFE1kQfP4oEp9E=",
            "function": "init",
            "arguments":  [],
            "match": True,
            "compiler.v.upto": 5
        }
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        if compiler.target_protocol < t.get("compiler.v.upto"):
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
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  function init(value : int) : state = { data = value }\n  function get() : int = state.data\n  stateful function set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+QYYRgKg9YdYcn5E3qBuiLxgjZ2rJv0YsOSknFA+gkbNeaVpfGf5BKX5AUmgOoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugeDc2V0uMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoP//////////////////////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////jJoEnsSQdsAgNxJqQzA+rc5DsuLDKUV7ETxQp+ItyJgJS3g2dldLhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA///////////////////////////////////////////uEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+QKLoOIjHWzfyTkW3kyzqYV79lz0D8JW9KFJiz9+fJgMGZNEhGluaXS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACg//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALkBoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQFEYgAAj2IAAMKRgICAUX9J7EkHbAIDcSakMwPq3OQ7LiwylFexE8UKfiLciYCUtxRiAAE5V1CAgFF/4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0QUYgAA0VdQgFF/OoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugcUYgABG1dQYAEZUQBbYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUpBZYABRWVJgAFJgAPNbYACAUmAA81tgAFFRkFZbYCABUVGQUIOSUICRUFCAWZCBUllgIAGQgVJgIJADYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUoFSkFCQVltgIAFRUVlQgJFQUGAAUYFZkIFSkFBgAFJZkFCQVltQUFlQUGIAAMpWhTMuMS4wZEveVQ==",
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACA6hZQte0c6B/XQTuHZwWpc6rFreRzqkolhGkTD+eW6BwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACoA4Uun",
            "function": "set",
            "arguments":  [42],
            "match": True,
            "compiler.v.upto": 4,
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  function init(value : int) : state = { data = value }\n  function get() : int = state.data\n  stateful function set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+QYYRgKg9YdYcn5E3qBuiLxgjZ2rJv0YsOSknFA+gkbNeaVpfGf5BKX5AUmgOoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugeDc2V0uMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoP//////////////////////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////jJoEnsSQdsAgNxJqQzA+rc5DsuLDKUV7ETxQp+ItyJgJS3g2dldLhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA///////////////////////////////////////////uEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+QKLoOIjHWzfyTkW3kyzqYV79lz0D8JW9KFJiz9+fJgMGZNEhGluaXS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACg//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALkBoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQFEYgAAj2IAAMKRgICAUX9J7EkHbAIDcSakMwPq3OQ7LiwylFexE8UKfiLciYCUtxRiAAE5V1CAgFF/4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0QUYgAA0VdQgFF/OoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugcUYgABG1dQYAEZUQBbYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUpBZYABRWVJgAFJgAPNbYACAUmAA81tgAFFRkFZbYCABUVGQUIOSUICRUFCAWZCBUllgIAGQgVJgIJADYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUoFSkFCQVltgIAFRUVlQgJFQUGAAUYFZkIFSkFBgAFJZkFCQVltQUFlQUGIAAMpWhTMuMS4wZEveVQ==",
            "function": "init",
            "arguments":  [42],
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACDiIx1s38k5Ft5Ms6mFe/Zc9A/CVvShSYs/fnyYDBmTRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACo7j+li",
            "match": True,
            "compiler.v.upto": 4,
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  entrypoint get() : int = state.data\n  stateful entrypoint set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+JFGA6DcSHcAbyhLqfbIDJRe1S7ZJLCZQJBUuvMmCLK5OirpHsC4YLg8/i+GW9kANwAHKCwAggD+RNZEHwA3AQc3AAwBACcMAhoCggEDP/7oxF62ADcBBzcADAEAJwwCGgKCAQM/ni8DES+GW9kNZ2V0EUTWRB8RaW5pdBHoxF62DXNldIIvAIk0LjAuMC1yYzUAFlcOUg==",
            "match": True,
            "compiler.v.upto": 5,
            "calldata": "cb_KxHoxF62G1Sy3bqn",
            "function": "set",
            "arguments":  [42],
        },
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
            "bytecode": "cb_+GpGA6Abk28ISckRxfWDHCo6FYfNzlAYCRW6TBDvQZ2BYQUmH8C4OZ7+RNZEHwA3ADcAGg6CPwEDP/64F37sADcBBwcBAQCWLwIRRNZEHxFpbml0EbgXfuwRbWFpboIvAIk0LjAuMC1yYzUAfpEWYw==",
            "match": True,
            "compiler.v.upto": 5,
            "calldata": "cb_KxG4F37sG1Q/+F7e",
            "function": "main",
            "arguments":  [42],
        }
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        if compiler.target_protocol < t.get("compiler.v.upto"):
            result = compiler.decode_calldata_with_bytecode(t.get("bytecode"), t.get('calldata'))
            print("RESULT", result)
            assert (t.get("match") and (
                result.function == t.get("function") and
                result.arguments[0].value == t.get("arguments")[0]
            ))


@pytest.mark.skip("to be verified")
def test_sophia_decode_calldata_sourcecode(compiler_fixture):
    tests = [
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  function get() : int = state.data\n  stateful function set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+QYYRgKg9YdYcn5E3qBuiLxgjZ2rJv0YsOSknFA+gkbNeaVpfGf5BKX5AUmgOoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugeDc2V0uMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoP//////////////////////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////jJoEnsSQdsAgNxJqQzA+rc5DsuLDKUV7ETxQp+ItyJgJS3g2dldLhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA///////////////////////////////////////////uEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+QKLoOIjHWzfyTkW3kyzqYV79lz0D8JW9KFJiz9+fJgMGZNEhGluaXS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACg//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALkBoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQFEYgAAj2IAAMKRgICAUX9J7EkHbAIDcSakMwPq3OQ7LiwylFexE8UKfiLciYCUtxRiAAE5V1CAgFF/4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0QUYgAA0VdQgFF/OoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugcUYgABG1dQYAEZUQBbYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUpBZYABRWVJgAFJgAPNbYACAUmAA81tgAFFRkFZbYCABUVGQUIOSUICRUFCAWZCBUllgIAGQgVJgIJADYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUoFSkFCQVltgIAFRUVlQgJFQUGAAUYFZkIFSkFBgAFJZkFCQVltQUFlQUGIAAMpWhTMuMS4wZEveVQ==",
            "function": "set",
            "sophia_value": 42,
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACA6hZQte0c6B/XQTuHZwWpc6rFreRzqkolhGkTD+eW6BwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACoA4Uun",
            "match": True,
            "compiler.v.upto": 4,
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  function get() : int = state.data\n  stateful function set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+QYYRgKg9YdYcn5E3qBuiLxgjZ2rJv0YsOSknFA+gkbNeaVpfGf5BKX5AUmgOoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugeDc2V0uMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoP//////////////////////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAC4YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP///////////////////////////////////////////jJoEnsSQdsAgNxJqQzA+rc5DsuLDKUV7ETxQp+ItyJgJS3g2dldLhgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA///////////////////////////////////////////uEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA+QKLoOIjHWzfyTkW3kyzqYV79lz0D8JW9KFJiz9+fJgMGZNEhGluaXS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACg//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALkBoAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEA//////////////////////////////////////////8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAYD//////////////////////////////////////////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAuQFEYgAAj2IAAMKRgICAUX9J7EkHbAIDcSakMwPq3OQ7LiwylFexE8UKfiLciYCUtxRiAAE5V1CAgFF/4iMdbN/JORbeTLOphXv2XPQPwlb0oUmLP358mAwZk0QUYgAA0VdQgFF/OoWULXtHOgf10E7h2cFqXOqxa3kc6pKJYRpEw/nlugcUYgABG1dQYAEZUQBbYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUpBZYABRWVJgAFJgAPNbYACAUmAA81tgAFFRkFZbYCABUVGQUIOSUICRUFCAWZCBUllgIAGQgVJgIJADYAAZWWAgAZCBUmAgkANgAFmQgVKBUllgIAGQgVJgIJADYAOBUoFSkFCQVltgIAFRUVlQgJFQUGAAUYFZkIFSkFBgAFJZkFCQVltQUFlQUGIAAMpWhTMuMS4wZEveVQ==",
            "function": "init",
            "sophia_value": 42,
            "calldata": "cb_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACA6hZQte0c6B/XQTuHZwWpc6rFreRzqkolhGkTD+eW6BwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACoA4Uun",
            "match": True,
            "compiler.v.upto": 4,
        },
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  entrypoint get() : int = state.data\n  stateful entrypoint set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+JFGA6DcSHcAbyhLqfbIDJRe1S7ZJLCZQJBUuvMmCLK5OirpHsC4YLg8/i+GW9kANwAHKCwAggD+RNZEHwA3AQc3AAwBACcMAhoCggEDP/7oxF62ADcBBzcADAEAJwwCGgKCAQM/ni8DES+GW9kNZ2V0EUTWRB8RaW5pdBHoxF62DXNldIIvAIk0LjAuMC1yYzUAFlcOUg==",
            "match": True,
            "compiler.v.upto": 5,
            "calldata": "cb_KxHoxF62G1Sy3bqn",
            "function": "set",
            "arguments":  [42],
        },
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
            "bytecode": "cb_+GpGA6Abk28ISckRxfWDHCo6FYfNzlAYCRW6TBDvQZ2BYQUmH8C4OZ7+RNZEHwA3ADcAGg6CPwEDP/64F37sADcBBwcBAQCWLwIRRNZEHxFpbml0EbgXfuwRbWFpboIvAIk0LjAuMC1yYzUAfpEWYw==",
            "match": True,
            "compiler.v.upto": 5,
            "calldata": "cb_KxG4F37sG1Q/+F7e",
            "function": "main",
            "arguments":  [42],
        }
    ]
    compiler = compiler_fixture.COMPILER
    for t in tests:
        if compiler.target_protocol < t.get("compiler.v.upto"):
            result = compiler.decode_calldata_with_sourcecode(t.get("sourcecode"), t.get('function'), t.get('calldata'))
            assert (t.get("match") and (
                result.function == t.get("function") and
                result.arguments[0].value == t.get("sophia_value")
            ))
