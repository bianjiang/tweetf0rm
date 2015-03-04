#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)

import redis, json
from tweetf0rm.utils import full_stack, hash_cmd, md5, get_keys_by_min_value

class RedisBase(object):

	def __init__(self, name, namespace='default', redis_config=None):
		if (not redis_config):
			redis_config = { 'host': 'localhost', 'port': 6379, 'db': 0}

		self.redis_config = redis_config
		self.__redis_connection = redis.StrictRedis(host=redis_config['host'], port=redis_config['port'], db=redis_config['db'])
		self.password = redis_config.get('password', None)
		self.namespace = namespace
		self.name = name
		self.key = '%s:%s'%(self.namespace, self.name)
		self.__auth()

	def get_key(self):
		return self.key

	def __auth(self):
		if self.password:
			self.__redis_connection.execute_command("AUTH", self.password)

	def conn(self):
		self.__auth()
		return self.__redis_connection

class RedisQueue(RedisBase):
	
	def __init__(self, name, queue_type='lifo', namespace='queue', redis_config=None):
		super(RedisQueue, self).__init__(name, namespace=namespace, redis_config=redis_config)
		if (queue_type not in ['fifo', 'lifo']):
			raise Exception("queue_type has to be either fifo or lifo")
		self.queue_type = queue_type

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
			if (self.queue_type == 'fifo'):
				item = self.conn().blpop(self.key, timeout=timeout)
			elif (self.queue_type == 'lifo'):
				item = self.conn().brpop(self.key, timeout=timeout)
		else:
			if (self.queue_type == 'fifo'):
				item = self.conn().lpop(self.key)
			elif (self.queue_type == 'lifo'):
				item = self.conn().rpop(self.key)

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

	def __init__(self, node_id, crawler_id, redis_config=None):
		super(CrawlerQueue, self).__init__('%s:%s'%(node_id,crawler_id), redis_config=redis_config)

class NodeQueue(RedisQueue):

	def __init__(self, node_id, redis_config=None):
		super(NodeQueue, self).__init__(node_id, redis_config=redis_config)
		self.node_id = node_id

	def clear_all_queues(self):
		'''This will not only clear the node queue (mostly for control cmds); but also the crawlers' cmd queues to give you a fresh start'''
		#self.conn().delete('queue:%s*'%(self.node_id))
		for key in self.conn().keys('queue:%s:*'%self.node_id):
			self.conn().delete(key)

		self.conn().delete('queue:%s'%self.node_id)

class NodeCoordinator(RedisBase):
	'''
	Used to coordinate queues across multiple nodes
	'''
	def __init__(self, redis_config=None):
		super(NodeCoordinator, self).__init__("coordinator", namespace="node", redis_config=redis_config)
		self.nodes_key = '%s:nodes'%(self.key)
		self.nodes = {}

	def get_node(self, node_id):
		if (node_id in self.nodes):
			node = self.nodes[node_id]
		else:
			node = NodeQueue(node_id, redis_config=self.redis_config)
			self.nodes[node_id] = node

		return node

	def distribute_to_nodes(self, crawler_queue):

		qsizes = self.node_qsizes()		

		cmd = crawler_queue.get(timeout=60)
		while (cmd):

			node_id = get_keys_by_min_value(qsizes)[0]

			node = self.get_node(node_id)			

			node.put(cmd)
			qsizes[node_id] += 1

			cmd = crawler_queue.get(timeout=60)

	def clear(self):
		self.conn().delete('%s:*'%self.key)

	def add_node(self, node_id):
		self.conn().sadd(self.nodes_key, node_id)

	def remove_node(self, node_id):
		''' Only remove the node from the active list;'''
		self.conn().srem(self.nodes_key, node_id)

	def list_nodes(self):
		node_ids = self.conn().smembers(self.nodes_key)
		return node_ids


	def node_qsizes(self):
		'''
		List the size of all active nodes' queues
		'''
		node_ids = self.conn().smembers(self.nodes_key)

		qsizes = {}
		for node_id in node_ids:
			qsize = 0
			for crawler_queue_key in self.conn().keys('queue:%s:*'%node_id):
				qsize += self.conn().llen(crawler_queue_key)	

			qsizes[node_id] = qsize

		return qsizes






