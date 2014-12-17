#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import logging

logger = logging.getLogger(__name__)

from .crawler_process import CrawlerProcess
from tweetf0rm.twitterapi.twitter_api import TwitterAPI
from tweetf0rm.handler import create_handler
from tweetf0rm.handler.crawl_user_relationship_command_handler import CrawlUserRelationshipCommandHandler
from tweetf0rm.utils import full_stack, hash_cmd
from tweetf0rm.exceptions import MissingArgs, NotImplemented
from tweetf0rm.redis_helper import NodeQueue
import copy, json


class TwitterCrawler(CrawlerProcess):

	def __init__(self, node_id, crawler_id, apikeys, handlers, redis_config, proxies=None):
		if (handlers == None):
			raise MissingArgs("you need a handler to write the data to...")

		super(TwitterCrawler, self).__init__(node_id, crawler_id, redis_config, handlers)

		self.apikeys = copy.copy(apikeys)
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
			"CRAWL_USER_TIMELINE": "fetch_user_timeline",
			"CRAWL_TWEET": "fetch_tweet_by_id",
			"SEARCH": "search_by_query"
		}
		self.node_queue = NodeQueue(self.node_id, redis_config=redis_config)
		self.client_args = {"timeout": 300}
		self.proxies = iter(proxies) if proxies else None
		self.twitter_api = None

		self.init_twitter_api()


	def init_twitter_api(self): # this will throw StopIteration if all proxies have been tried...
		if (self.proxies):
			try:
				self.client_args['proxies'] = next(self.proxies)['proxy_dict'] # this will throw out 
				#logger.info("client_args: %s"%json.dumps(self.client_args))
			except StopIteration as exc:
				raise
			except Exception as exc:
				self.init_twitter_api()

		if (self.twitter_api):
			del self.twitter_api

		#crawler_id=self.crawler_id, 
		self.twitter_api = TwitterAPI(apikeys=self.apikeys, client_args=self.client_args)


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

			command = cmd['cmd']

			logger.debug("new cmd: %s"%(cmd))

			redis_cmd_handler = None

			#maybe change this to a map will be less expressive, and easier to read... but well, not too many cases here yet...
			if (command == 'TERMINATE'):
				# make sure we need to flush all existing data in the handlers..
				for handler in self.handlers:
				 	handler.flush_all()
				break
			elif (command == 'CRAWLER_FLUSH'):
				for handler in self.handlers:
				 	handler.flush_all()
			else:

				# figure out args first...
				args = {}
				if (command == 'CRAWL_TWEET'):
					args = {
						"tweet_id": cmd['tweet_id'],
						"write_to_handlers": self.handlers,
						"cmd_handlers" : []
					}
				elif (command == 'SEARCH'):
					args = {
						"write_to_handlers": self.handlers,
						"cmd_handlers" : []
					}
				else:
					args = {
						"user_id": cmd['user_id'],
						"write_to_handlers": self.handlers,
						"cmd_handlers" : []
					}

				bucket = cmd["bucket"] if "bucket" in cmd else None

				if (bucket):
					args["bucket"] = bucket
				
				func = None
				if  (command in ['CRAWL_USER_TIMELINE', 'CRAWL_TWEET']):
					func = getattr(self.twitter_api, self.tasks[command])
				elif (command in ['SEARCH']):

					if "lang" in cmd:
						args['lang'] = cmd['lang']

					if "geocode" in cmd:
						args['geocode'] = cmd['geocode']

					if "key" in cmd:
						args['key'] = cmd['key']

					#logger.info("new cmd: %s"%(cmd))
					# q is required, otherwise let it fail...
					if "query" in cmd:
						args['query'] = cmd['query']
						func = getattr(self.twitter_api, self.tasks[command])


				elif (command in ['CRAWL_FRIENDS', 'CRAWL_FOLLOWERS']):
					data_type = cmd['data_type']
					
					try:
						depth = cmd["depth"] if "depth" in cmd else None
						depth = int(depth)
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
							args["cmd_handlers"].append(CrawlUserRelationshipCommandHandler(template=template, redis_config=self.redis_config))

							logger.info("depth: %d, # of cmd_handlers: %d"%(depth, len(args['cmd_handlers'])))

					except Exception as exc:
						logger.warn(exc)
					
					func = getattr(self.twitter_api, self.tasks[command][data_type])
				
				if func:
					try:
						#logger.info(args)
						func(**args)
						del args['cmd_handlers']
						for handler in self.handlers:
				 			handler.flush_all()						
					except Exception as exc:
						logger.error("%s"%exc)
						try:
							self.init_twitter_api()
						except StopIteration as init_twitter_api_exc:
							# import exceptions
							# if (isinstance(init_user_api_exc, exceptions.StopIteration)): # no more proxy to try... so kill myself...
							for handler in self.handlers:
			 					handler.flush_all()

			 				logger.warn('not enough proxy servers, kill me... %s'%(self.crawler_id))
			 				# flush first
							self.node_queue.put({
								'cmd':'CRAWLER_FAILED',
								'crawler_id': self.crawler_id
								})
							del self.node_queue
							return False
							#raise
						else:
							#put current task back to queue...
							logger.info('pushing current task back to the queue: %s'%(json.dumps(cmd)))
							self.enqueue(cmd)

						#logger.error(full_stack())
						
				else:
					logger.warn("whatever are you trying to do?")

		logger.info("looks like i'm done...")
			
		return True


			



			