#!/bin/bash
# Functions and env variable for working with aeternity
#
# You just need to set EPOCH_HOME and have a normal config there and
# the scripts will do the rest for you.

# Copyright (c) 2018 aeternity developers

# Permission to use, copy, modify, and/or distribute this software for
# any purpose with or without fee is hereby granted, provided that the
# above copyright notice and this permission notice appear in all
# copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA
# OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

function aepub_key {
	echo `curl -s http://127.0.0.1:$AE_LOCAL_INTERNAL_PORT/v2/account/pub-key|jq '.pub_key'|sed -e 's/\"//g'`
}

export AE_PUB_KEY=`aepub_key`

alias aecd="cd $EPOCH_HOME"
#alias aebalance="curl -sG http://127.0.0.1:$AE_LOCAL_INTERNAL_PORT/v2/account/balance/`aepub_key`|jq .balance"

function aebalance {
    PUB_KEY=`aepub_key`
    curl -sG "http://127.0.0.1:$AE_LOCAL_INTERNAL_PORT/v2/account/balance/${PUB_KEY}" | jq .balance
}

function aespend-tx {
    if [ "$#" -ne 3 ]; then
	echo "Usage: aespend-tx recipient_pub_key amount fee"
    else
	curl -X POST -H 'Content-Type: application/json' -d "{\"recipient_pubkey\":\"$1\", \"amount\":$2, \"fee\":$3}" http://127.0.0.1:$AE_LOCAL_INTERNAL_PORT/v2/spend-tx
    fi
}

