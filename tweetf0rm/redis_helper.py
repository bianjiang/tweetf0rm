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
		self.__auth()
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

class NodeQueue(RedisQueue):

	def __init__(self, node_id, redis_config=None):
		super(NodeQueue, self).__init__(node_id, redis_config=redis_config)

class NodeCoordinator(RedisBase):
	'''
	Used to coordinate queues across multiple nodes
	'''
	def __init__(self, redis_config=None):
		super(NodeCoordinator, self).__init__("coordinator", namespace="node", redis_config=redis_config)

	def clear(self):
		self.conn().delete(self.key)

	def add_node(self, node_id):
		self.conn().sadd(self.key, node_id)

	def remove_node(self, node_id):
		self.conn().srem(self.key, node_id)

	def node_queue_key(self, node_id):
		return 'queue:%s'%(node_id)

	def node_qsizes(self):
		'''
		List the size of all node queues
		'''
		node_ids = self.conn().smembers(self.key)

		logger.info(node_ids)

		qsizes = {node_id:self.conn().llen(self.node_queue_key(node_id)) for node_id in node_ids}

		return qsizes






