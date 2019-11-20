==========================
Account management via CLI
==========================

The Python SDK comes with a command line client (CLI) that can be used
among other things to generate, store, inspect and load accounts


Generate a new account
======================

The command to generate a new (non HD) account is:

::
  
  $ aecli account create KEYSTORE_FILENAME.json
  

the command will ask for a password and will store the account in the file 
named ``KEYSTORE_FILENAME.json``; here an example:

::

  ➜ aecli account create  BOB.json
  Enter the account password []: 
  <account>
    Address ___________________________________________ ak_2P44NhGFT7fP1TFpZ62FwabWP9djg5sDwFNDVVpiGgd3p4yA7X
    Path ______________________________________________ /howto/BOB.json
  </account>

Print the secret key of an account
==================================

.. warning::
  The secret key is printed in "clear text", by printing it on the terminal or saving
  it unencrypted you expose your account


the command to print the public and secret key of an account saved in a keystore file is:

::
  
  $ aecli account address --secret-key KEYSTORE_FILENAME.json

Example:

::

  ➜ aecli account address BOB.json --secret-key
  Enter the account password: 
  !Warning! this will print your secret key on the screen, are you sure? [y/N]: y
  <account>
    Address ___________________________________________ ak_2P44NhGFT7fP1TFpZ62FwabWP9djg5sDwFNDVVpiGgd3p4yA7X
    Secretkey _________________________________________ c226bf650f30740287f77a715............f49ddff758971112fb5cfb0e66975a8f
  </account>


