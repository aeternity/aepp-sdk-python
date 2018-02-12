#!/usr/bin/python

"""Simple post office for aeternity. Registers a free oracle which
accepts mails in the JSON format { "action": "<action>" "rcpt":
"pub_key recipient", "body": "text to send or contents" } where action
is one of 'send' or 'recv', and rcpt and body are only required
for sending.

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
import dbm.gnu
import json
import sys

oracle = Oracle()

with dbm.gnu.open('mail.gdbm', 'c') as db:

    def respond(data):
        mail = json.loads(data['payload']['query'])
        print(mail)
        action = mail['action']
        sender = data['payload']['sender']
        if action == "send":
            recipient = mail['rcpt']
            print("rcpt: " + recipient)
            body = mail['body']
            existing = []
            try:
                existing = json.loads(db[recipient])
            except KeyError:
                pass
            existing.append(json.dumps({"from": sender, "body": body}))
            db[recipient] = json.dumps(existing)
            oracle.respond(data['payload']['query_id'], 5, "Mail sent")
        else: # receive
            mail = []
            try:
                mail = json.loads(db[sender])
            except KeyError:
                pass
            oracle.respond(data['payload']['query_id'], 3, json.dumps(mail))
            db[sender] = "[]"
            db.sync
            
            
    oracle_id = oracle.register("mail2", "mail", 0, 2000, 6)
    oracle.subscribe(oracle_id, respond)
