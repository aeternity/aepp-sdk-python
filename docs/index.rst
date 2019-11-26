.. aepp-sdk documentation master file, created by
   sphinx-quickstart on Mon Nov 11 23:04:48 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Aeternty Python SDK Documentation (aepp-sdk)
============================================

.. rubric:: Everything you need to know about the Aeternity Python SDK.

.. toctree::
   :hidden:
   
   intro/index
   howto/index
   topics/index
   ref/index
   faq/index
   snippets/index


How the documentation is organized
==================================

A high-level overview of how it's organized will help you know 
where to look for certain things:

* :doc:`Tutorials </intro/index>` take you by the hand through a series of
  steps to create a python aepp. Start here if you're new to Aeternity
  application development. Also look at the ":ref:`index-first-steps`" below.

* :doc:`Topic guides </topics/index>` discuss key topics and concepts at a
  fairly high level and provide useful background information and explanation.

* :doc:`Reference guides </ref/index>` contain technical reference for APIs and
  other aspects of Aeternity SDK machinery. They describe how it works and how to
  use it but assume that you have a basic understanding of key concepts.

* :doc:`How-to guides </howto/index>` are recipes. They guide you through the
  steps involved in addressing key problems and use-cases. They are more
  advanced than tutorials and assume some knowledge of how the Aeternity SDK works.

* :doc:`Code snippets </snippets/index>` are various pieces of codes to copy/paste.
  They may be useful to find pieces of codes to get stuff done.

.. _index-first-steps:

First steps
===========

Are you new to the Aeternity SDK? This is the place to start!

* **From scratch:**

  * :doc:`Installation <intro/install>`

* **Tutorial:**

  * :doc:`Spend transactions <intro/tutorial01-spend>`
  * :doc:`Deploy a contract <intro/tutorial02-contracts-deploy>`
  * :doc:`Call a contract <intro/tutorial02-contracts-call>`
  * :doc:`Claiming a name <intro/tutorial03-aens>`
  * :doc:`Using Generalized accounts <intro/tutorial04-ga>`
  * :doc:`The CLI <intro/tutorial05-cli>`


* **How to:**

  * Coming soon...

..  * :doc:`Generate a list of accounts on the fly <howto/accounts>`
  * :doc:`Use the json output from the CLI with jq <howto/json_jq>`
  * :doc:`Pretty print amounts <howto/amounts>`

* **Reference:**

  * :doc:`The NodeClient and Config <ref/client_and_config>`
  * :doc:`The TxObject <ref/txobject>`


Getting help
============

Having trouble? We'd like to help!

* Try the :doc:`FAQ <faq/index>` -- it's got answers to many common questions.

* Looking for specific information? Try the :ref:`genindex` or :ref:`modindex`
  
* Search for information in the `Aeternity forum`_, or `post a question`_.

* Report bugs with the Python SDK in our `issue tracker`_.

.. _Aeternity forum: https://forum.aeternity.com
.. _post a question: https://forum.aeternity.com
.. _issue tracker: https://github.com/aeternity/aepp-sdk-python/issues


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

