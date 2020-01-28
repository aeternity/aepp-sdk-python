from aeternity.contract_native import ContractNative
import aeternity.hashing


contract = """contract DelegateTest =
  // Transactions
  stateful payable entrypoint signedPreclaim(addr  : address,          // Claim on behalf of this account (can be Contract.address)
                                             chash : hash,             // Commitment hash
                                             sign  : signature) : unit = // Signed by addr (if not Contract.address)
    AENS.preclaim(addr, chash, signature = sign)

  stateful entrypoint signedClaim(addr : address,
                                name : string,
                                salt : int,
                                sign : signature) : unit =
    AENS.claim(addr, name, salt, 360000000000000000000, signature = sign)


  stateful entrypoint signedUpdate(owner      : address,
                                   name       : string,
                                   ttl        : option(Chain.ttl),
                                   client_ttl : option(int),
                                   pointers   : option(map(string, AENS.pointee)),
                                   sign       : signature) : unit =
    AENS.update(owner, name, ttl, client_ttl, pointers, signature = sign)


  stateful entrypoint signedTransfer(owner     : address,
                                   new_owner : address,
                                   name      : string,
                                   sign      : signature) : unit =
    AENS.transfer(owner, new_owner, name, signature = sign)

  stateful entrypoint signedRevoke(owner     : address,
                                   name      : string,
                                   sign      : signature) : unit =
    AENS.revoke(owner, name, signature = sign)

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


def test_contract_signature_delegation(compiler_fixture, chain_fixture):
    compiler = compiler_fixture.COMPILER
    account = chain_fixture.ALICE
    bob = chain_fixture.BOB
    contract_native = ContractNative(client=chain_fixture.NODE_CLI, source=contract, compiler=compiler, account=account)
    contract_native.deploy()

    assert(contract_native.address is not None)

    # the contract_id
    contract_id = contract_native.address
    # node client
    node_cli = contract_native.client

    # example name
    name = "anexampledomainname.chain"
    salt = 987654321
    committment_id = hashing.committment_id(name, salt)
    name_ttl = 500000
    client_ttl = 36800
    pointers = {"account_id": account.get_address()}

    # aens calls
    signature = client.delegate_name_preclaim_signature(account, contract_id)
    _, call_result = contract_native.signed_preclaim(account.get_address(), committment_id, signature)
    assert(call_result > 0)

    signature = client.delegate_name_claim_signature(account, contract_id, name)
    _, call_result = contract_native.signed_claim(account.get_address(), name, salt, signature)
    assert(call_result > 0)

    signature = client.delegate_name_update_signature(account, contract_id, name)
    _, call_result = contract_native.signed_claim(account.get_address(), name, name_ttl, client_ttl, pointers, signature)
    assert(call_result > 0)

    signature = client.delegate_name_transfer_signature(account, contract_id, name)
    _, call_result = contract_native.signed_transfer(account.get_address(), bob.get_address(), name, signature)
    assert(call_result > 0)

    signature = client.delegate_name_revoke_signature(bob, contract_id, name)
    _, call_result = contract_native.signed_revoke(bob.get_address(), name, signature)
    assert(call_result > 0)

    # oracle calls



