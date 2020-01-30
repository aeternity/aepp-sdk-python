from aeternity.contract_native import ContractNative
from aeternity import hashing, utils
from tests.conftest import random_domain
import pytest


contractAens = """contract DelegateTest =
  // Transactions
  stateful payable entrypoint signedPreclaim(addr  : address,
                                             chash : hash,
                                             sign  : signature) : unit =
    AENS.preclaim(addr, chash, signature = sign)

  stateful entrypoint signedClaim(addr : address,
                                name : string,
                                salt : int,
                                name_fee : int,
                                sign : signature) : unit =
    AENS.claim(addr, name, salt, name_fee, signature = sign)


  stateful entrypoint signedTransfer(owner     : address,
                                   new_owner : address,
                                   name      : string,
                                   sign      : signature) : unit =
    AENS.transfer(owner, new_owner, name, signature = sign)

  stateful entrypoint signedRevoke(owner     : address,
                                   name      : string,
                                   sign      : signature) : unit =
    AENS.revoke(owner, name, signature = sign)
"""


@pytest.mark.skip("blocked by https://github.com/aeternity/aepp-sdk-python/issues/306")
def test_node_contract_signature_delegation(compiler_fixture, chain_fixture):
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    bob = chain_fixture.BOB
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=contractAens, compiler=compiler, account=account)
    contract_native.deploy()

    assert(contract_native.address is not None)

    # the contract_id
    contract_id = contract_native.address
    # node client
    ae_cli = contract_native.client

    # example name
    name = random_domain(length=15)
    c_id, salt = hashing.commitment_id(name, 9876)
    name_ttl = 500000
    client_ttl = 36000
    name_fee = utils.amount_to_aettos("20AE")
    print(f"name is {name}, commitment_id: {c_id}")

    # aens calls
    signature = ae_cli.delegate_name_preclaim_signature(account, contract_id)
    call, r = contract_native.signedPreclaim(account.get_address(), hashing.decode(c_id), signature)
    assert(call.return_type == 'ok')
    ae_cli.wait_for_confirmation(call.tx_hash)

    signature = ae_cli.delegate_name_claim_signature(account, contract_id, name)
    call, _ = contract_native.signedClaim(account.get_address(), name, salt, name_fee, signature)
    assert(call.return_type == 'ok')

    signature = ae_cli.delegate_name_transfer_signature(account, contract_id, name)
    call, _ = contract_native.signedTransfer(account.get_address(), bob.get_address(), name, signature)
    assert(call.return_type == 'ok')

    signature = ae_cli.delegate_name_revoke_signature(bob, contract_id, name)
    call, _ = contract_native.signedRevoke(bob.get_address(), name, signature)
    assert(call.return_type == 'ok')



contractOracles = """contract DelegateTest =
  type fee = int
  type ttl = Chain.ttl

  type query_t  = string
  type answer_t = int

  type oracle_id = oracle(query_t, answer_t)
  type query_id  = oracle_query(query_t, answer_t)

  stateful payable entrypoint signedRegisterOracle(acct : address,
                                                   sign : signature,
                                                   qfee : fee,
                                                   ttl  : ttl) : oracle_id =
     Oracle.register(acct, qfee, ttl, signature = sign)

  stateful payable entrypoint signedExtendOracle(o    : oracle_id,
                                                 sign : signature,   // Signed oracle address
                                                 ttl  : ttl) : unit =
    Oracle.extend(o, signature = sign, ttl)

  datatype complexQuestion = Why(int) | How(string)
  datatype complexAnswer   = NoAnswer | Answer(complexQuestion, string, int)

  stateful entrypoint signedComplexOracle(question, sig) =
    let o = Oracle.register(signature = sig, Contract.address, 0, FixedTTL(1000)) : oracle(complexQuestion, complexAnswer)
    let q = Oracle.query(o, question, 0, RelativeTTL(100), RelativeTTL(100))
    Oracle.respond(o, q, Answer(question, "magic", 1337), signature = sig)
    Oracle.get_answer(o, q)
"""

