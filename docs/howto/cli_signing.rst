==========================
Account management via CLI
==========================

The Python SDK comes with a command line client (CLI) that 
exposes, among others, the ability to sign transactions and arbitrary data.

This how-to assumes that you are familiar with the Aeternity accounts.

.. note::
  in the examples it is assumed that there is present an account keystore file: ``ALICE.json``,
  refer to the accounts how-to about how to generate the keystore.
  In the example the Alice account has the address ``ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M``


Let's start generating a spend transaction

::
  
  ➜ aecli tx spend ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M ak_BobY97QUVR4iDLg4k3RKmy6shZYx9FR75nLaN33GsVmSnhWxn 10ae --nonce 42   
  <spend tx>
    <data>
      Tag _____________________________________________ 12
      Version _________________________________________ 1
      Recipient id ____________________________________ ak_BobY97QUVR4iDLg4k3RKmy6shZYx9FR75nLaN33GsVmSnhWxn
      Amount __________________________________________ 10AE
      Fee _____________________________________________ 0.00001682AE
      Sender id _______________________________________ ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
      Payload _________________________________________ ba_Xfbg4g==
      Ttl _____________________________________________ 0
      Nonce ___________________________________________ 42
    </data>
    <metadata>
      Min fee _________________________________________ 0.00001682AE
    </metadata>
    Tx ________________________________________________ tx_+FkMAaEBE9B4l/BeyxMO//3ANxwyT+ZHL52j9nAZosRe/YFuK4ehARiHxowOzuxowMG/Kz6Vsp2zc6afObhytg1uz3EaiUGbiIrHIwSJ6AAAhg9MNiAIAAAqgJO0CS0=
    Hash ______________________________________________ th_Y4CnFrmCkSPu7QBnF5jXw1HGuhtUhToaqK6LfEEQwvB1yyhdA
  </spend tx>

Sign a transaction
==================

In this section Alice uses the encoded transaction string to sign the transaction and create a signed transaction

::

  ➜ aecli account sign ALICE.json tx_+FkMAaEBE9B4l/BeyxMO//3ANxwyT+ZHL52j9nAZosRe/YFuK4ehARiHxowOzuxowMG/Kz6Vsp2zc6afObhytg1uz3EaiUGbiIrHIwSJ6AAAhg9MNiAIAAAqgJO0CS0= 
  Enter the account password: 
  <signed transaction>
    <data>
      Tag _____________________________________________ 11
      Version _________________________________________ 1
      <signatures 1>
        Signature #1 __________________________________ sg_GBf8w2rLiJbU3Ze1LjtqkYCZSoqhskb4RcMjyUyquqo7NoBLTCXqykaqBFbQAixns59QAGTDhbBjLwdafybJPMvQ2YuaL
      </signatures>
      <tx>
        <data>
          Tag _________________________________________ 12
          Type ________________________________________ SpendTx
          Version _____________________________________ 1
          Sender id ___________________________________ ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
          Recipient id ________________________________ ak_BobY97QUVR4iDLg4k3RKmy6shZYx9FR75nLaN33GsVmSnhWxn
          Amount ______________________________________ 10AE
          Fee _________________________________________ 0.00001682AE
          Ttl _________________________________________ 0
          Nonce _______________________________________ 42
          Payload _____________________________________ ba_Xfbg4g==
        </data>
        <metadata>
          Min fee _____________________________________ 0.00001682AE
        </metadata>
        Tx ____________________________________________ tx_+FkMAaEBE9B4l/BeyxMO//3ANxwyT+ZHL52j9nAZosRe/YFuK4ehARiHxowOzuxowMG/Kz6Vsp2zc6afObhytg1uz3EaiUGbiIrHIwSJ6AAAhg9MNiAIAAAqgJO0CS0=
      </tx>
    </data>
    <metadata>
      Network id ______________________________________ ae_mainnet
    </metadata>
    Tx ________________________________________________ tx_+KMLAfhCuEB0DvcFHJGpJkDutkDmMCHin7oxA9Vpfvx9Wm+MUCBSz/15Th7BZQSBB+4CLDQVGUnStLl/IRKnlk8LllpTV98FuFv4WQwBoQET0HiX8F7LEw7//cA3HDJP5kcvnaP2cBmixF79gW4rh6EBGIfGjA7O7GjAwb8rPpWynbNzpp85uHK2DW7PcRqJQZuIiscjBInoAACGD0w2IAgAACqAvRFPSA==
    Hash ______________________________________________ th_FXdkE1cBqfPinv3Vjwq32Bs1R5KFyhmREATiSSGqQhDYnQhdx
  </signed transaction>


Sign arbitrary data
===================

the command to print the public and secret key of an account saved in a keystore file is:

::

  ➜ aecli account sign-data ALICE.json tx_+FkMAaEBE9B4l/BeyxMO//3ANxwyT+ZHL52j9nAZosRe/YFuK4ehARiHxowOzuxowMG/Kz6Vsp2zc6afObhytg1uz3EaiUGbiIrHIwSJ6AAAhg9MNiAIAAAqgJO0CS0=  
  Enter the account password: 
  <data signature>
    Account ___________________________________________ ak_9j8akv2PE2Mnt5khFeDvS9BGc3TBBrJkfcgaJHgBXcLLagX8M
    Signature _________________________________________ sg_PP6CFZjKUTwyBUa7eabNMn826qXfDBcZ4tfp2xktPqZo47boHJB2bsuVcc3EhhSAZaHZFr9cPDfoTY8hckLKEacb9HpdQ
  </data signature>

.. attention::
  Even if the input for the two commands (sign and sign-data) is the same, the resulting signature is different since the data is modified before being signed (TODO: add a topic about the signture generation)


