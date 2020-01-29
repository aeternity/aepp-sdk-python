=======
Amounts
=======

The Aeternity blockchain tokens are an ERC-20 compatible token,
where the unit is the Aetto (1e-18).

The ``utils`` submodule provides functions to manipulate the 
amounts.


Format amount to a human readable format
========================================

The following snippets show how to format
an amount from ``aetto`` to a human readable format.

::
  
  # import the utils submodule
  from aeternity import utils

  amount = 1000000000000000000
  human_value = utils.format_amount(amount)
  print(human_value) # prints 1AE


Parse amounts
=============

This snippets shows how to parse amounts 
expressed in a human friendly, float or scientific notation.

::
  
  # import the utils submodule
  from aeternity import utils

  amount = utils.amount_to_aettos(1.2)
  print(amount) # prints 1200000000000000000

  amount = utils.amount_to_aettos("10AE")
  print(amount) # prints 10000000000000000000

  amount = utils.amount_to_aettos(1e1)
  print(amount) # prints 10000000000000000000

  amount = utils.amount_to_aettos(1)
  print(amount) # prints 1


.. Important::
  when using amount_to_aettos function, the maximum value as imput is 1e9,
  that will result in an aetto value of 1000000000000000000000000000 (1e27).
  Bigger values wil return in an error.



