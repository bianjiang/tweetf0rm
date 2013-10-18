#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
RedisCommandHandler: handler that generates new commands on the fly
'''

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from .base_handler import BaseHandler
import multiprocessing as mp
import futures, json, copy, time
from tweetf0rm.redis_helper import CrawlerQueue, CrawlerCoordinator
from tweetf0rm.utils import full_stack
from tweetf0rm.scheduler import distribute_to
import json

def flush_cmd(bulk, data_type, template, redis_config, verbose=False):

	try:

		crawler_coordinator = CrawlerCoordinator(redis_config=redis_config)

		qsizes = crawler_queue.list_qsize()
		
		crawler_queues = {}

		for element in bulk:
			if data_type == "ids" and type(element) == int:
				user_id = element
			elif data_type =="users" and type(element) == dict and "id" in element:
				user_id = element['id']
			
			t = copy.copy(template)
			t["user_id"] = user_id
			t["depth"] -= 1

			c_id = distribute_to(qsizes)[0]

			if (c_id in crawler_queues):
				crawler_queue = crawler_queues[c_id]
			else:
				crawler_queue = CrawlerQueue(c_id, redis_config=redis_config)
				crawler_queues[c_id] = crawler_queue

			crawler_queue.put(t)
			qsizes[c_id] += 1

			if verbose:
				logger.info("send [%s] to %s"%(json.dumps(t),c_id))

			
	except:
		logger.error(full_stack())

	return True
		

class CrawlUserRelationshipCommandHandler(BaseHandler):

	def __init__(self, verbose=False, template=None, redis_config = None):
		'''
		A RedisCommandHandler is used to push new commands into the queue;
		this is helpful, in cases such as crawling a user's followers' followers to create a network
		some user has extremely large number of followers, it's impossible (and inefficient) to re-iterate through 
		the follower lists, after it's done... when it flush, it flush the commands to the redis channel
		'''
		super(CrawlUserRelationshipCommandHandler, self).__init__(verbose=verbose)
		self.data_type = template["data_type"]
		self.template = template
		self.redis_config = redis_config

	def need_flush(self, bucket):
		# flush every time there is new data comes in
		return True

	def flush(self, bucket):
		logger.info("i'm getting flushed...")

		with futures.ProcessPoolExecutor(max_workers=1) as executor:
			for k, v in self.buffer[bucket].iteritems():
				for s in v:
					o = json.loads(s)

					f = executor.submit(flush_cmd, o[self.data_type], self.data_type, self.template, self.redis_config, verbose=self.verbose)

					self.futures.append(f)
					# while (f.running()):
					# 	time.sleep(5)
			
			# send to a different process to operate, clear the buffer
			self.clear(bucket)

		True

