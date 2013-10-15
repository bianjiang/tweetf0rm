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

class CrawlUserRelationshipCommandHandler(BaseHandler):

	def __init__(self, verbose=False, template=None):
		'''
		A RedisCommandHandler is used to push new commands into the queue;
		this is helpful, in cases such as crawling a user's followers' followers to create a network
		some user has extremely large number of followers, it's impossible (and inefficient) to re-iterate through 
		the follower lists, after it's done... when it flush, it flush the commands to the redis channel
		'''
		super(RedisCommandHandler, self).__init__(verbose=verbose)
		self.network_type = template["network_type"]
		self.data_type = template["data_type"]

	def check_flus(self):

	def __flush_process(self):

	def flus(self):
		func = getattr(self, "__flush_process")
		with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:

			for k, v in self.buffer[self.network_type].iteritems():
				for s in v:
					o = json.loads(v)
					for user_ids in o[self.data_type]:
						if type(user_ids) == list:
							logger.info(user_ids)
				#executor.submit(func, )
				
		pass

