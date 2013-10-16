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
from tweetf0rm.redis_helper import RedisQueue
from tweetf0rm.utils import full_stack

def flush_cmd(bulk, data_type, template, redis_config):
	try:
		redis_cmd_queue = RedisQueue(name="cmd", redis_config=redis_config)

		for element in bulk:
			if data_type == "ids" and type(element) == int:
				user_id = element
			elif data_type =="users" and type(element) == dict and "id" in element:
				user_id = element['id']
			
			t = copy.copy(template)
			t["user_id"] = user_id
			t["depth"] -= 1

			redis_cmd_queue.put(t)
	except:
		logger.error(full_stack())

	logger.info("number of command in queue: %d"%redis_cmd_queue.qsize())

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
		self.result_bucket = template["result_bucket"]
		self.data_type = template["data_type"]
		self.template = template
		self.redis_config = redis_config

	def need_flush(self):
		return True

	def flush(self):
		logger.info("i'm getting flushed...")

		with futures.ProcessPoolExecutor(max_workers=1) as executor:
			for k, v in self.buffer[self.result_bucket].iteritems():
				for s in v:
					o = json.loads(s)

					f = executor.submit(flush_cmd, o[self.data_type], self.data_type, self.template, self.redis_config)
					while (f.running()):
						time.sleep(5)
				# 
				# 	o = json.loads(v)
				# 	for user_ids in o[self.data_type]:
				# 		if type(user_ids) == list:
				# 			logger.info(user_ids)
				#executor.submit(func, )
				
		pass

