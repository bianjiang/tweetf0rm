#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
base_handler.py: handlers are the sinks of data
'''

import logging

logger = logging.getLogger(__name__)

from tweetf0rm.exceptions import WrongArgs
import json

class BaseHandler(object):

	def __init__(self):
		'''
			buckets: defines the sub-structure of the buffer; either ["tweets", "followers", "follower_ids", "friends", "friend_ids", "timelines"]
		'''
		self.buffer = dict()
		self.buckets = ["tweets", "followers", "follower_ids", "friends", "friend_ids", "timelines"]
		for bucket in self.buckets:
			self.buffer[bucket] = dict()
		self.futures = []

	def append(self, data=None, bucket=None, key='current_timestampe'):
		if (not data):
			raise WrongArgs("what's the point? not data coming in...")

		if (bucket not in self.buckets):
			raise WrongArgs("%s is not a valid buckets..."%bucket)

		logger.debug("adding new data -- into [%s][%s]"%(bucket, key))

		if (key not in self.buffer[bucket]):
			self.buffer[bucket][key] = list()
			
		self.buffer[bucket][key].append(data)

		need_flush = self.need_flush(bucket)
		logger.debug("flush? %s"%need_flush)
		if (need_flush):
			self.flush(bucket)


	def get(self, bucket, key):
		return self.buffer[bucket][key]

	def stat(self):
		stat = {}
		for bucket in self.buckets:
			stat[bucket] = {
				'count': len(self.buffer[bucket])
			}

			data = {}
			for k in self.buffer[bucket]:
				data[k] = len(self.buffer[bucket][k])
			
			stat[bucket]["data"] = data
		
		return stat

	def remove_key(self, bucket = None, key = None):
		del self.buffer[bucket][key]

	def clear(self, bucket = None):
		if (bucket):
			logger.debug("clear bucket: %s"%bucket)
			del self.buffer[bucket]
			self.buffer[bucket] = dict()

	def clear_all(self):
		for bucket in self.buckets:
			self.clear(bucket)

	def need_flush(self, bucket):
		'''
		sub-class determine when to flush and what to flush
		'''
		pass

	def flush(self, bucket):
		logger.info('calling the BaseHandler flush???')
		pass

	def flush_all(self, block=False):

		for bucket in self.buffer:
			self.flush(bucket)

		if (block):
			for f in self.futures:
				while(not f.done()):
					time.sleep(5)

		return True

