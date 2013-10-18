#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.INFO)

import redis, json

class RedisBase(object):

	def __init__(self, name, namespace='default', redis_config=None):
		if (not redis_config):
			redis_config = { 'host': 'localhost', 'port': 6379, 'db': 0}

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
		self.conn().rpush(self.key, json.dumps(item))

	def get(self, block=True, timeout=None):
		"""Remove and return an item from the queue. 

		If optional args block is true and timeout is None (the default), block
		if necessary until an item is available."""
		if block:
			item = self.conn().blpop(self.key, timeout=timeout)
		else:
			item = self.conn().lpop(self.key)

		if item:
			item = json.loads(item[1])
		return item

	def get_nowait(self):
		"""Equivalent to get(False)."""
		return self.get(False)

	def clear(self):
		"""Clear out the queue"""
		self.conn().delete(self.key)

class CrawlerQueue(RedisQueue):

	def __init__(self, crawler_id, redis_config=None):
		super(RedisQueue, self).__init__(crawler_id, redis_config=redis_config)

class CrawlerCoordinator(RedisBase):
	'''
	Used to coordinate queues across multiple nodes
	'''
	def __init__(self, redis_config=None):
		super(CrawlerQueueStat, self).__init__("coordinator", namespace="crawler", redis_config=redis_config)

	def add_crawler(self, crawler_id):
		self.conn().sadd(self.key, crawler_id)

	def remove_crawler(self, crawler_id):
		self.conn().srem(self.key, crawler_id)

	def crawler_queue_key(self, crawler_id):
		return 'queue:%s'%(crawler_id)

	def list_crawler_qsize(self):
		'''
		List the size of all queues
		'''
		crawler_ids = self.conn().smembers(self.key)

		qsizes = {crawler_id:self.conn().llen(self.crawler_queue_key(crawler_id)) for crawler_id in crawler_ids}

		return qsizes






