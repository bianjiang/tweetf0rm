#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.INFO)

import redis

class RedisBase(object):

	def __init__(self, name, namespace='default', redis_config=None):
		self.__redis_connection = redis.StrictRedis(host=redis_config['host'], port=redis_config['port'], db=redis_config['db'])
		self.password = redis_config['password']
		self.namespace = namespace
		self.name = name
		self.key = '%s:%s'%(self.namespace, self.name)
		if (self.password):
			self.__auth()


	def __auth(self):
		self.__redis_connection.execute_command("AUTH", self.password)

	def conn(self):
		return self.__redis_connection

class RedisQueue(RedisBase):

	def __init__(self, name, namespace='queue', redis_config=None):
		super(RedisQueue, self).__init__(name, namespace=namespace, redis_config=redis_config)

	def qsize(self):
		"""Return the approximate size of the queue."""
		return self.conn().llen(self.key)

	def empty(self):
		"""Return True if the queue is empty, False otherwise."""
		return self.qsize() == 0

	def put(self, item):
		"""Put item into the queue."""
		self.conn().rpush(self.key, item)

	def get(self, block=True, timeout=None):
		"""Remove and return an item from the queue. 

		If optional args block is true and timeout is None (the default), block
		if necessary until an item is available."""
		if block:
			item = self.conn().blpop(self.key, timeout=timeout)
		else:
			item = self.conn().lpop(self.key)

		if item:
			item = item[1]
		return item

	def get_nowait(self):
		"""Equivalent to get(False)."""
		return self.get(False)

	def clear(self):
		"""Clear out the queue"""
		self.conn().delete(self.key)

