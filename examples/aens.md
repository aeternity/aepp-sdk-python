# Aens

This example will show how to claim a name using the python sdk

## Programmatically

TODO

# CLI

Register a name using the cli

### Step 1: pre-claim

```
$ aecli name pre-claim rea abcsdads.test
Enter the account password:
<preclaim transaction>
  <data>
    Tag _____________________________________________ 33
    Vsn _____________________________________________ 1
    Account id ______________________________________ ak_REAu6DK8eqW5juKhGKTZo7svi1EcKxAsu7vq6yRUaNw4K6Ypg
    Nonce ___________________________________________ 1
    Commitment id ___________________________________ cm_2j44A8k8BrM7i3bF8daP3G6GEKcRxnJR5Dmhpb4XBbKFUGcLiw
    Fee _____________________________________________ 16660000000000
    Ttl _____________________________________________ 0
  </data>
  <metadata>
    Salt ____________________________________________ 2506137870146646926
  </metadata>
  Tx ________________________________________________ tx_+JkLAfhCuEB55SXB1T4Ky58B5p93LJ+AxRrPK86JkHsjrGcHm40k64ISb2q5Sw86pSl76xBJRx4/hiGoP1CiZugUPzn6SLQFuFH4TyEBoQE3ArNgfdSENAyDj62+HrTamcCQMBT3YS6Do12LJb96/QGhA+MuiyIt2sbqyUTNiDsi2beVwzRZtAwg3qdu4en3foqYhg8m9WHIAABg1TjO
  Hash ______________________________________________ th_EtkGeA8fSMgBSD4QkR2mbDBd6tMSDTFX9ydKfHT5kwkAjWmbF
  Signature _________________________________________ sg_GwwtULX1Y1CNB8Jpxz7XKx6opZ8TidEEZPaTrcKtfULvMuCiYpBjPp5H7shfRRMmNGSRQzQyfWSQen8YUgrPmiipAUbL6
  Network id ________________________________________ ae_mainnet
</preclaim transaction>
```

Inspect the transaction:

```
 $ aecli inspect th_EtkGeA8fSMgBSD4QkR2mbDBd6tMSDTFX9ydKfHT5kwkAjWmbF
<transaction>
  Block hash ________________________________________ mh_UdXT6AZaAAp1B8GBy3qcyKzYJ29mJEVZ7KRh4JWBLE5GJUSCR
  Block height ______________________________________ 46893
  Hash ______________________________________________ th_EtkGeA8fSMgBSD4QkR2mbDBd6tMSDTFX9ydKfHT5kwkAjWmbF
  <signatures 1>
    Signature #1 ____________________________________ sg_GwwtULX1Y1CNB8Jpxz7XKx6opZ8TidEEZPaTrcKtfULvMuCiYpBjPp5H7shfRRMmNGSRQzQyfWSQen8YUgrPmiipAUbL6
  </signatures>
  <tx>
    Account id ______________________________________ ak_REAu6DK8eqW5juKhGKTZo7svi1EcKxAsu7vq6yRUaNw4K6Ypg
    Commitment id ___________________________________ cm_2j44A8k8BrM7i3bF8daP3G6GEKcRxnJR5Dmhpb4XBbKFUGcLiw
    Fee _____________________________________________ 16660000000000
    Nonce ___________________________________________ 1
    Type ____________________________________________ NamePreclaimTx
    Version _________________________________________ 1
  </tx>
</transaction>
```

### Step 2: claim

Run the claim contract immediately will fail

```
 $ aecli name claim rea abcsdads.test  --name-salt=2506137870146646926 --preclaim-tx-hash=th_EtkGeA8fSMgBSD4QkR2mbDBd6tMSDTFX9ydKfHT5kwkAjWmbF
Enter the account password:
<error>
  Message ___________________________________________ It is not safe to execute the name claim before height 46896, current height: 46893
</error>
```

This happens because it is not safe to send a claim transaction before making sure the pre-claim is confirmed.
The claim operation exposes the actual domain been registered and if a preclaim has not been confirmed the domain 
name could be squatted.


After waiting the the height has been reached:

```
 $ aecli chain top
 $ aecli chain top
<top for node at https://sdk-mainnet.aepps.com >
  Beneficiary _______________________________________ ak_542o93BKHiANzqNaFj6UurrJuDuxU61zCGr9LJCwtTUg34kWt
  Hash ______________________________________________ kh_zkMD8E8ttzKE5nVswAfmhQNcmwWWxhFsJ7xt5c4A2NC2am3ij
  Height ____________________________________________ 46896
  Miner _____________________________________________ ak_2f5T1WYcbLBxifqtBBi4ZNrMbUUfaFyhxJcupyHqJBMWRvYrWA
  Nonce _____________________________________________ 113778650302622
  Prev hash _________________________________________ kh_C9v4tKCj54Qhcstg5H2fRAZpXKSoG4sv5U7Ged697PYJ6wvRP
  Prev key hash _____________________________________ kh_C9v4tKCj54Qhcstg5H2fRAZpXKSoG4sv5U7Ged697PYJ6wvRP
  State hash ________________________________________ bs_Z8ohBeRtZ72VyWaqZZCPzQhjrjTtoBDwbpUSXCtc4HpTymdHS
  Target ____________________________________________ 503658739
  Time ______________________________________________ 2019-03-05T15:53:14.494000+00:00
  Version ___________________________________________ 1
</top for node at https://sdk-mainnet.aepps.com >

```

It is safe to claim the name:

```
 $ aecli name claim rea abcsdads.test  --name-salt=2506137870146646926 --preclaim-tx-hash=th_EtkGeA8fSMgBSD4QkR2mbDBd6tMSDTFX9ydKfHT5kwkAjWmbF
Enter the account password:
<name abcsdads.test claim transaction>
  <data>
    Tag _____________________________________________ 32
    Vsn _____________________________________________ 1
    Account id ______________________________________ ak_REAu6DK8eqW5juKhGKTZo7svi1EcKxAsu7vq6yRUaNw4K6Ypg
    Nonce ___________________________________________ 2
    Name ____________________________________________ abcsdads.test
    Name salt _______________________________________ 2506137870146646926
    Fee _____________________________________________ 16440000000000
    Ttl _____________________________________________ 0
  </data>
  Metadata
  Tx ________________________________________________ tx_+I4LAfhCuEA7HGDR5TMHWErNQcQuML1bHTwBYWtMXAmNqyTTZMikhZ37SythjjUPdX2RfWfQ/id+Sg3d8HMjHJtfyThDSecAuEb4RCABoQE3ArNgfdSENAyDj62+HrTamcCQMBT3YS6Do12LJb96/QKNYWJjc2RhZHMudGVzdIgix5cdZD6zjoYO87xcMAAAP5EMUg==
  Hash ______________________________________________ th_hmYqc3BDeTqLMw2Ti6eotGSU53DBpiG2Gngm5pt4aJXtqfGDp
  Signature _________________________________________ sg_8jY6iqQuPejk5divU4wD4TF9Xq4RJxKmYQd8Rnve7yy5AJJP7QT5XLKKvVYih64ECBU5XoscUdbySmL2XPtxCxZM1vT96
  Network id ________________________________________ ae_mainnet
</name abcsdads.test claim transaction>
 $
```

And to inspect it:
```
$ aecli inspect abcsdads.test                                                                                                                                                                       ✔  10060  2019-03-05T17:00 
<name>
  Id ________________________________________________ nm_2RLergfp7jmg18aaU1JL5NMm4fJhqhSqN9HbG6AqZikm575NqK
  <pointers 0>
  </pointers>
  Ttl _______________________________________________ 96896
</name>
```