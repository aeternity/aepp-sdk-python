===================
Quick install guide
===================

Before you can use the Aeternity SDK, you'll need to get it installed. 
This guide will guide you to a minimal installation that'll work
while you walk through the introduction. For more installation options  
check the :doc:`installation guide </topics/install>`.


Install Python
==============

Get the latest version of Python at https://www.python.org/downloads/ or with
your operating system's package manager.

You can verify that Python is installed by typing ``python`` from your shell;
you should see something like::

    Python 3.7.y
    [GCC 4.x] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

.. hint::
  The mimimum required python version is 3.6 but 3.7 is recommended!


Install the SDK 
====================

The Aeternity Python SDK package name is ``aepp-sdk``  and it is available
via the `pypi.org`_ repository.

.. _pypi.org: https://pypi.org/project/aepp-sdk/

To install or upgrade run the command

::

  pip install -U aepp-sdk


Verifying
=========

To verify that the Aeternity SDK  can be seen by Python, type ``python`` from your shell.
Then at the Python prompt, try to import aeternity:

.. parsed-literal::

    >>> import aeternity
    >>> print(aeternity._version())
    |version|


To verify that the CLI is available in your ``PATH`` run the command 

.. parsed-literal::

    $ aecli --version
    aecli, version |version|





That's it!
==========

That's it -- you can now :doc:`move onto the tutorial </intro/tutorial01-spend>`.
