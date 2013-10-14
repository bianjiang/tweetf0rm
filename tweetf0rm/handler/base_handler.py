#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
base_handler.py: handlers are the sinks of data
'''

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from tweetf0rm.exceptions import WrongArgs
import json

class BaseHandler(object):

	def __init__(self, verbose=False):
		'''
			data_type: defines the sub-structure of the buffer; either ["tweets", "followers", "friends", "timelines"]
		'''
		
		self.buffer = {}
		self.data_types = ["tweets", "followers", "follower_ids", "friends", "friend_ids", "timelines"]
		for data_type in self.data_types:
			self.buffer[data_type] = {}
		logger.info(self.buffer)
		self.verbose = verbose

	def append(self, data=None, data_type=None, key='current_timestampe'):
		if (not data):
			raise WrongArgs("what's the point? not data coming in...")

		if (data_type not in self.data_types):
			raise WrongArgs("%s is not a valid data_type..."%data_type)

		if (self.verbose):
			#logger.info("adding data -- [%s] into [%s][%s]"%(json.dumps(data), data_type, key))
			logger.info("adding new data -- into [%s][%s]"%(data_type, key))

		if (key not in self.buffer[data_type]):
			self.buffer[data_type][key] = []
			
		self.buffer[data_type][key].append(data)

	def get(self, data_type, key):
		return self.buffer[data_type][key]

	def stat(self):
		stat = {}
		for data_type in self.data_types:
			stat[data_type] = {
				'count': len(self.buffer[data_type])
			}

			data = {}
			for k in self.buffer[data_type]:
				data[k] = len(self.buffer[data_type][k])
			
			stat[data_type]["data"] = data
		
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


