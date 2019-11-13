===============================
Keystore format change [LEGACY]
===============================

The release 0.25.0.1 of the Python SDK change the format of the keystore used to store
a secret key in an encrypted format.

The previous format, suported till version ``0.25.0.1b1`` is not supported anymore and secret keys
encrypted with the legacy format will have to be updated manually.

.. warning:: ⚠️ BEFORE YOU START

   The following procedure will print your secret key unencrypted on the terminal.

   **Make sure you perform this procedure in a secret setting.**



The follwing steps are required to upgade a keystore (named `my_account.json`).

#. Install the `aepp-sdk` v0.25.0.1b1

::
   
  $ pip install aepp-sdk==0.25.0.1b1

Verify that you are using the correct version

::
  
  $ aecli --version
  aecli, version 0.25.0.1b1

#. Print your secret key to the terminal

::
    
  aecli account address --secret-key my_account.json
  Enter the account password []:
  !Warning! this will print your secret key on the screen, are you sure? [y/N]: y
  <account>
    Address ___________________________________________ ak_2UeaQn7Ei7HoMvDTiq2jyDuE8ymEQMPZExzC64qWTxpUnanYsE
    Signing key _______________________________________ 507f598f2fac1a4ab57edae53650cbf7ffae9eeeea1a297cc7c3b6172052e55ec27954c4ba901cf9b3760dc12b2c313d60fcc674ba2d04746ed813a91499a2ed
  </account>

#. Install the `aepp-sdk` v0.25.0.1

::
  
  $ pip install aepp-sdk==0.25.0.1

Verify that you are using the correct version

::

  $ aecli --version
  aecli, version 0.25.0.1

#. Save the secret key to the new format

::
  
  aecli account save my_account_new.json 507f598f2fac1a4ab57edae53650cbf7ffae9eeeea1a297cc7c3b6172052e55ec27954c4ba901cf9b3760dc12b2c313d60fcc674ba2d04746ed813a91499a2ed
  Enter the account password []:
  <account>
    Address ___________________________________________ ak_2UeaQn7Ei7HoMvDTiq2jyDuE8ymEQMPZExzC64qWTxpUnanYsE
    Path ______________________________________________ /Users/andrea/tmp/aeternity/my_account_new.json
  </account>

5. Verify that the new keystore has the correct format

the content of the keystore file should appear as the following:

::
  
  $ cat my_account_new.json
  {"public_key": "ak_2UeaQn7Ei7HoMvDTiq2jyDuE8ymEQMPZExzC64qWTxpUnanYsE", "crypto": {"secret_type": "ed25519", "symmetric_alg": "xsalsa20-poly1305", "ciphertext": "f431af7e6f00da7f9acc8187900b97d42526eb135f4db0da80a7809f36a00e37f3a313f7c611784f381e58620bb2c23ef2686c3e61af28381f3a2dc6b0fcc168d46fd8d3c2bd473311140b7ee5acaa2d", "cipher_params": {"nonce": "1ea25d885a68adf13998e0fad17b22e7ade78f5cf1670eb1"}, "kdf": "argon2id", "kdf_params": {"memlimit_kib": 262144, "opslimit": 3, "salt": "c3dd4a4ac8347b3ad706756b96919387", "parallelism": 1}}, "id": "44c3d693-a890-4ac1-936b-0a65c8293388", "name": "", "version": 1}

6. Cleanup!

Once the operation is completed, cleanup the terminaly history that contains
your secret key

:: 
  
  history -c

And remove the old account file

::
  
  rm my_account.json
