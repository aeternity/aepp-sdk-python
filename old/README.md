# aeternity-dev-tools

## Introduction

This repo is for tools and notes for working with aeternity when you're running an epoch node on your local machine.

## aeternity-functions.sh

This script is intended to be called from your .bashrc like this:

`. /path/to/aeternity-functions.sh`

It will parse your `epoch.yaml` (clumsily, needs improvement), and set the environment variables `AE_LOCAL_PORT` and `AE_LOCAL_INTERNAL_PORT`. It has a dependency on [jq] (https://stedolan.github.io/jq/).

### Functions and aliases provided, variables exported

`aepub_key` calls the internal port and parses the result, returning the public key.
`aeupdate_pub_key` exports the result of calling `aepub_key` into the variable `AE_PUB_KEY`.
`aecd` changes to the epoch working directory.
`aebalance` returns the current balance.
`aespend-tx` transfers given currency to a pub key, with fee (`aespend-tx recipient amount fee`)

`AE_PUB_KEY` is exported for general use.

