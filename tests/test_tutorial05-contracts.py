from . import conftest

"""
WARINING: this file is used as source for the tutorial in
docs/intro/tutorial05-contracts.rst
line numbers are important
verify the doc file for consistency after edit
"""
import os

from aeternity.node import NodeClient, Config
from aeternity.compiler import CompilerClient
from aeternity.contract_native import ContractNative
from aeternity.signing import Account

def test_example_contract_native(chain_fixture):

    NODE_URL = os.environ.get('TEST_URL', 'http://127.0.0.1:3013')
    NODE_INTERNAL_URL = os.environ.get('TEST_DEBUG_URL', 'http://127.0.0.1:3113')
    COMPILER_URL = os.environ.get('TEST_COMPILER__URL', 'https://compiler.aepps.com')

    node_cli = NodeClient(Config(
        external_url=NODE_URL,
        internal_url=NODE_INTERNAL_URL,
        blocking_mode=True,
    ))

    compiler = CompilerClient(compiler_url=COMPILER_URL)

    sender_account = chain_fixture.ALICE

    # genrate ALICE account (and transfer AE to alice account)
    alice = Account.generate()

    node_cli.spend(sender_account, alice.get_address(), 5000000000000000000)

    CONTRACT_FILE = os.path.join(os.path.dirname(__file__), "testdata/CryptoHamster.aes")

    # read contract file
    with open(CONTRACT_FILE, 'r') as file:
        crypto_hamster_contract = file.read()

    """
    Initialize the contract instance
    Note: To disable use of dry-run endpoint add the parameter
    use_dry_run=False
    """
    crypto_hamster = ContractNative(client=node_cli, 
                                    compiler=compiler, 
                                    account=alice, 
                                    source=crypto_hamster_contract)

    # deploy the contract 
    # (also pass the args of thr init function - if any)
    tx = crypto_hamster.deploy()
    print(f"contract address: {crypto_hamster.address}")


    # PART 2 Call the contract
    CONTRACT_ID = crypto_hamster.address

    # CONTRACT_ID is the address of the deployed contract 
    crypto_hamster.at(CONTRACT_ID)

    # call the contract method (stateful)
    tx_info, tx_result = crypto_hamster.create_hamster("SuperCryptoHamster")

    print(f"Transaction Hash: {tx_info.tx_hash}")
    print(f"Transaction Result/Return Data: {tx_result}")

    
    assert(hasattr(tx_info, 'tx_hash'))

    # call contract method (not stateful)
    tx_info, tx_result = crypto_hamster.get_hamster_dna("SuperCryptoHamster", None)

    print(f"Transaction Result/Return Data: {tx_result}")

    assert tx_result is not None
    assert not hasattr(tx_info, 'tx_hash')
        
