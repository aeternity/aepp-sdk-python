#!/usr/bin/python

"""
A class for aeternity oracle clients and servers.
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

from oracle import Oracle
import sys

oracle = Oracle()
def respond(data):
    oracle.respond(data['payload']['query_id'], 5, "Response!")

query_format, response_format, query_fee, ttl, fee = sys.argv[1:6]
oracle_id = oracle.register(query_format, response_format, query_fee, ttl, fee)
oracle.subscribe(oracle_id, respond)
