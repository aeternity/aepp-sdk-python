import pytest
from pytest import skip

#
# SOPHIA
#


def _sophia_contract_tx_create_online(node_cli, account):
    tests = [
        {
            # init(42)
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  entrypoint get() : int = state.data\n  stateful entrypoint set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+JFGA6CaF4v9syrdOevYZSWs8H6yoVk//r4Azu+V96W3B5CXFMC4YLg8/i+GW9kANwAHKCwAggD+RNZEHwA3AQc3AAwBACcMAhoCggEDP/7oxF62ADcBBzcADAEAJwwCGgKCAQM/ni8DES+GW9kNZ2V0EUTWRB8RaW5pdBHoxF62DXNldIIvAIk0LjAuMC1yYzUAYj/1oA==",
            "calldata": "cb_KxFE1kQfG1TH2kjs",
        },
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
            "bytecode": "cb_+GpGA6Abk28ISckRxfWDHCo6FYfNzlAYCRW6TBDvQZ2BYQUmH8C4OZ7+RNZEHwA3ADcAGg6CPwEDP/64F37sADcBBwcBAQCWLwIRRNZEHxFpbml0EbgXfuwRbWFpboIvAIk0LjAuMC1yYzUAfpEWYw==",
            "calldata": "cb_KxFE1kQfP4oEp9E=",  # init()
        }

    ]
    for t in tests:
        contract = node_cli.Contract()
        tx = contract.create(account, t.get("bytecode"), calldata=t.get("calldata"), gas=100000)
        c_id = tx.metadata.contract_id
        deployed = node_cli.get_contract(pubkey=c_id)
        assert deployed.active is True
        assert deployed.owner_id == account.get_address()


def _sophia_contract_tx_call_online(node_cli, account):
    tests = [
        {
            "name": "simplestorage.aes",
            "sourcecode": "contract SimpleStorage =\n  record state = { data : int }\n  entrypoint init(value : int) : state = { data = value }\n  entrypoint get() : int = state.data\n  stateful entrypoint set(value : int) = put(state{data = value})\n",
            "bytecode": "cb_+JFGA6CaF4v9syrdOevYZSWs8H6yoVk//r4Azu+V96W3B5CXFMC4YLg8/i+GW9kANwAHKCwAggD+RNZEHwA3AQc3AAwBACcMAhoCggEDP/7oxF62ADcBBzcADAEAJwwCGgKCAQM/ni8DES+GW9kNZ2V0EUTWRB8RaW5pdBHoxF62DXNldIIvAIk0LjAuMC1yYzUAYj/1oA==",
            # init(42)
            "init.calldata": "cb_KxFE1kQfG1TH2kjs",
            "call.function": "set",
            "call.arguments": [24],
            "call.calldata": "cb_KxHoxF62GzAP+Odz",
            "return.value": "cb_P4fvHVw="  # 0,
        },
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
            "bytecode": "cb_+GpGA6Abk28ISckRxfWDHCo6FYfNzlAYCRW6TBDvQZ2BYQUmH8C4OZ7+RNZEHwA3ADcAGg6CPwEDP/64F37sADcBBwcBAQCWLwIRRNZEHxFpbml0EbgXfuwRbWFpboIvAIk0LjAuMC1yYzUAfpEWYw==",
            "init.calldata": "cb_KxFE1kQfP4oEp9E=",
            "call.function": "main",
            "call.arguments": [42],
            "call.calldata": "cb_KxG4F37sG1Q/+F7e",
            "return.value": "cb_VNLOFXc="  # 42

        }

    ]
    for t in tests:
        print(f"call contract {t.get('name')}")
        contract = node_cli.Contract()
        tx = contract.create(account, t.get("bytecode"), calldata=t.get("init.calldata"))
        c_id = tx.metadata.contract_id
        deployed = node_cli.get_contract(pubkey=c_id)
        assert deployed.active is True
        assert deployed.owner_id == account.get_address()
        tx = contract.call(c_id, account, t.get("call.function"), t.get("call.calldata"))
        # retrieve the call object
        call = contract.get_call_object(tx.hash)
        assert call.return_value == t.get("return.value")
        assert call.return_type == "ok"

def _sophia_contract_tx_call_static(node_cli, account):
    tests = [
        {
            "name": "identity.aes",
            "sourcecode": "contract Identity =\n  entrypoint main(x : int) = x",
            "bytecode": "cb_+GpGA6Abk28ISckRxfWDHCo6FYfNzlAYCRW6TBDvQZ2BYQUmH8C4OZ7+RNZEHwA3ADcAGg6CPwEDP/64F37sADcBBwcBAQCWLwIRRNZEHxFpbml0EbgXfuwRbWFpboIvAIk0LjAuMC1yYzUAfpEWYw==",
            "init.calldata": "cb_KxFE1kQfP4oEp9E=",
            "call.function": "main",
            "call.arguments": [42],
            "call.calldata": "cb_KxG4F37sG1Q/+F7e",
            "return.value": "cb_VNLOFXc="  # 42

        }

    ]
    for t in tests:
        contract = node_cli.Contract()
        tx = contract.create(account, t.get("bytecode"), calldata=t.get("init.calldata"))
        c_id = tx.metadata.contract_id
        deployed = node_cli.get_contract(pubkey=c_id)
        assert deployed.active is True
        assert deployed.owner_id == account.get_address()
        tx = contract.call_static(c_id, t.get("call.function"), t.get("call.calldata"), address=account.get_address())
        assert tx.result == "ok"

def test_sophia_contract_tx_create_native_lima(chain_fixture):
    # save settings and go online
    _sophia_contract_tx_create_online(chain_fixture.NODE_CLI, chain_fixture.ALICE)


def test_sophia_contract_tx_call_native_lima(chain_fixture):
    # save settings and go online
    _sophia_contract_tx_call_online(chain_fixture.NODE_CLI, chain_fixture.ALICE)
    # restore settings

def test_sophia_contract_tx_call_static_native_lima(chain_fixture):
    # save settings and go online
    _sophia_contract_tx_call_static(chain_fixture.NODE_CLI, chain_fixture.BOB)
    # restore settings


