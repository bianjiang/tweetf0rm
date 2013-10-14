#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
base_handler.py: handlers are the sinks of data
'''

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

import time, os, sys, threading, futures

class BaseHandler(object):

	def __init__(self, verbose=False):
		'''
			data_type: defines the sub-structure of the buffer; either ["tweets", "followers", "friends", "timelines"]
		'''
		self.buffer = {}
		self.data_types = ["tweets", "followers", "friends", "timelines"]
		for data_type in self.data_types:
			self.buffer[data_type] = {}
		self.verbose = verbose

	def stat(self):
		stat = {}
		for data_type in self.data_types:
			stat[data_type] = {
				'count': len(self.buffer[data_type])
			}
		return stat

	def remove_key(self, data_type = None, key = None):
		del self.buffer[data_type][key]

	def clear(self, data_type = None):
		del self.buffer[data_type]

	def clear_all(self):
		for data_type in self.data_types:
			self.clear(data_type)

	def flush(self, key):
		pass

	def close(self, key):
		pass

	def close(self):		
		pass