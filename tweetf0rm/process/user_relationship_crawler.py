#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from .crawler_process import CrawlerProcess
from tweetf0rm.twitterapi.users import User
from tweetf0rm.handler import create_handler
from tweetf0rm.handler.crawl_user_relationship_command_handler import CrawlUserRelationshipCommandHandler
from tweetf0rm.utils import full_stack, hash_cmd
from tweetf0rm.exceptions import MissingArgs, NotImplemented
from tweetf0rm.redis_helper import NodeQueue
import copy, json


class UserRelationshipCrawler(CrawlerProcess):

	def __init__(self, node_id, crawler_id, apikeys, handlers = None, verbose = False, redis_config = None, proxies=None):
		if (handlers == None):
			raise MissingArgs("you need a handler to write the data to...")
		super(UserRelationshipCrawler, self).__init__(crawler_id, handlers=handlers, verbose=verbose)
		self.redis_config = redis_config
		self.apikeys = copy.copy(apikeys)
		self.node_id = node_id
		self.tasks = {
			"TERMINATE": "TERMINATE", 
			"CRAWL_FRIENDS" : {
				"users": "find_all_friends",
				"ids": "find_all_friend_ids",
				"network_type": "friends"
			},
			"CRAWL_FOLLOWERS" :{
				"users": "find_all_followers",
				"ids": "find_all_follower_ids",
				"network_type": "followers"
			}, 
			"CRAWL_USER_TIMELINE": "fetch_user_timeline"
		}
		self.node_queue = NodeQueue(self.node_id, redis_config=redis_config)		
		self.client_args = {"timeout": 300}
		self.proxies = iter(proxies) if proxies else None
		self.user_api = None
		self.init_user_api()

	def init_user_api(self): # this will throw StopIteration if all proxies have been tried...
		if (self.proxies): 
			self.client_args['proxies'] = next(self.proxies) # this will throw out 

		if (self.user_api):
			del self.user_api

		self.user_api = User(apikeys=self.apikeys, verbose=self.verbose, client_args=self.client_args)

	def get_handlers(self):
		return self.handlers

	def avaliable_cmds(self):
		return self.tasks.keys()

	def run(self):
		while True:
			# cmd is in json format
			# cmd = {
			#	network_type: "followers", # or friends
			#	user_id: id,
			#	data_type: 'ids' # users
			#}
			cmd = self.get_cmd()

			if self.verbose:
				logger.info("new cmd: %s"%(cmd))

			command = cmd['cmd']

			cmd_hash = hash_cmd(cmd)

			redis_cmd_handler = None

			#maybe change this to a map will be less expressive, and easier to read... but well, not too many cases here yet...
			if (command == 'TERMINATE'):
				# make sure we need to flush all existing data in the handlers..
				for handler in self.handlers:
				 	handler.flush_all()
				break
			else:

				args = {
					"user_id": cmd['user_id'],
					"write_to_handlers": self.handlers,
				}

				bucket = cmd["bucket"] if "bucket" in cmd else None

				if (bucket):
					args["bucket"] = bucket
				
				func = None
				if  (command == 'CRAWL_USER_TIMELINE'):
					func = getattr(self.user_api, self.tasks[command])
				elif (command in ['CRAWL_FRIENDS', 'CRAWL_FOLLOWERS']):
					data_type = cmd['data_type']
					depth = cmd["depth"] if "depth" in cmd else None

					logger.info("depth: %d"%(depth))
					# for handler in self.handlers:
					# 	if isinstance(handler, InMemoryHandler):
					# 		inmemory_handler = handler
					if (depth > 1):
						template = copy.copy(cmd)
						# template = {
						#	network_type: "followers", # or friends
						#	user_id: id,
						#	data_type: 'ids' # object
						#	depth: depth
						#}
						# will throw out exception if redis_config doesn't exist...
						args["write_to_handlers"].append(CrawlUserRelationshipCommandHandler(verbose=False, template=template, redis_config=self.redis_config))
					
					func = getattr(self.user_api, self.tasks[command][data_type])
				
				if func:
					try:
						func(**args)
					except Exception as exc:
						logger.error("%s"%exc)
						try:
							self.init_user_api()
						except Exception as init_user_api_exc:
							import exceptions
							if (isinstance(init_user_api, exceptions.StopIteration)): # no more proxy to try... so kill myself...
								for handler in self.handlers:
				 					handler.flush_all()
				 				# flush first
								self.node_queue.put({
									'cmd':'CRAWLER_FAILED',
									'crawler_id': self.crawler_id
									})
							return False
							#raise
						else:
							#put current task back to queue...
							self.enqueue(cmd)

						#logger.error(full_stack())
					else:
						self.node_queue.put({'cmd':"CMD_FINISHED", "cmd_hash":cmd_hash, "crawler_id":self.crawler_id})
				else:
					logger.warn("whatever are you trying to do?")

		if self.verbose:
			logger.info("looks like i'm done...")
			# for handler in self.handlers:
			# 	logger.info(handler.stat())

			
		return True


			



			