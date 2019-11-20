================================
How to install the Aeternity SDK
================================

This document will explain differnet way to install the Aeternity Python SDK


Install Python
==============

Get the latest version of Python at https://www.python.org/downloads/ or with your operating system’s package manager.


Install the SDK
===============

Installation instructions are slightly different depending on whether you're
installing official relase or fetching the latest development version.

.. _installing-official-release:

Installing an official release with ``pip``
-------------------------------------------

This is the recommended way to install the Aeternity SDK

#. Install pip_. The easiest is to use the `standalone pip installer`_. If your
   distribution already has ``pip`` installed, you might need to update it if
   it's outdated. If it's outdated, you'll know because installation won't
   work.

#. Take a look at virtualenv_ and virtualenvwrapper_. These tools provide
   isolated Python environments, which are more practical than installing
   packages systemwide. They also allow installing packages without
   administrator privileges. The :doc:`contributing tutorial
   </intro/contributing>` walks through how to create a virtualenv.

#. After you've created and activated a virtual environment, enter the command:

::

        $ python -m pip install aepp-sdk

.. _pip: https://pip.pypa.io/
.. _virtualenv: https://virtualenv.pypa.io/
.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _standalone pip installer: https://pip.pypa.io/en/latest/installing/#installing-with-get-pip-py

.. _installing-distribution-package:


Installing the development version
----------------------------------

If you'd like to be able to update your SDK code occasionally with the
latest bug fixes and improvements, follow these instructions:

#. Make sure that you have Git_ installed and that you can run its commands
   from a shell. (Enter ``git help`` at a shell prompt to test this.)

#. Install Poetry_ and make sure it is available in your ``PATH``


#. Check out the SDK main development branch like so:

::

        $ git clone https://github.com/aeternity/aepp-sdk-python.git

This will create a directory ``aepp-sdk-python`` in your current directory.

#. Make sure that the Python interpreter can load the SDK's code. The most
   convenient way to do this is to use virtualenv_, virtualenvwrapper_, and
   pip_. 

#. After setting up and activating the virtualenv, run the following command:

::

        $ poetry build 
        $ python -m pip install dist/$(ls -tr dist | grep whl | tail -1)

This will make the SDK code importable, and will also make the
``aecli`` utility command available. In other words, you're all set!

.. _Poetry: https://poetry.eustace.io/

When you want to update your copy of the SDK source code, run the command
``git pull`` from within the ``aepp-sdk-directory`` directory. When you do this, Git will
download any changes.


.. admonition:: Where is the command line client?

    The Python SDK bundles a command line client ``aecli`` that can be use to submit 
    transactions and poke around the Aeternity blockchain. 
    To be able to access the command line client you have to add it to your executable 
    path. To find out where is your base path for installed python libraries use the command
    ``python -m site --user-base``


