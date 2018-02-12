#!/usr/bin/python

"""
A class for aeternity oracle clients and servers.
Author: John Newby

(c) Ape Unit 2018
"""

from epoch import Epoch
import sys

epoch = Epoch()

epoch.wait_for_block()

