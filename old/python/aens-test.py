#!/usr/bin/python

"""
Test of Æternity Naming System
Author: John Newby

Copyright (c) 2018 aeternity developers

Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted, provided that the
above copyright notice and this permission notice appear in all
copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

from aens import AENS
import json 
import sys

aens = AENS()

domain, commitment = sys.argv[1:3]

if aens.query(domain) != None:
    print("Domain " + domain + " already registered")

result = aens.pre_claim(commitment, 1)
print("Pre-claim result: " + result)
aens.wait_for_block()
name_hash = aens.claim(domain, 123, 1)

print("Claim result: " + name_hash)
aens.wait_for_block()
result = aens.query(domain)
if result != None:
    print("Query result now: " + json.dumps(result))
else:
    print("NO NO NO")

aens.wait_for_block
result = aens.update(aens.get_pub_key(), name_hash)
print("Update result: " + result)
aens.wait_for_block()
result = aens.query(domain)
if result != None:
    print("Query result now: " + json.dumps(result))
else:
    print("NO NO NO")
    
result = aens.revoke(name_hash)
print("Revoke result: " + result)
aens.wait_for_block()
result = aens.query(domain)
if result != None:
    print("Query result now: " + json.dumps(result))
else:
    print("Domain now unregistered")
    
