#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from .worker_process import WorkerProcess
from tweetf0rm.twitterapi.users import User
from tweetf0rm.exceptions import MissingArgs, NotImplemented
import copy, json


class UserRelationshipCrawler(WorkerProcess):

	def __init__(self, apikeys, handlers = None, verbose = False, proxy=None):
		if (handlers == None):
			raise MissingArgs("you need a handler to write the data to...")
		super(UserRelationshipCrawler, self).__init__(handlers=handlers, verbose=verbose)
		self.apikeys = copy.copy(apikeys)
		if (proxy):
			client_args={'proxies':{'http':'http://%s'%proxy}}
		else:
			client_args = None
		self.user_api = User(apikeys=apikeys, verbose=verbose, client_args=client_args)
		self.proxy = proxy
		if (self.verbose):
			logger.info("# of handlers: %d"%(len(self.get_handlers())))
		self.tasks = {
			"TERMINATE": "TERMINATE", 
			"CRAWL_FRIENDS" : {
				"object": "find_all_friends",
				"id": "find_all_friend_ids"
			},
			"CRAWL_FOLLOWERS" :{
				"object": "find_all_followers",
				"id": "find_all_follower_ids"
			}, 
			"CRAWL_USER_TIMELINE": "fetch_user_timeline"
		}

	def get_handlers(self):
		return self.handlers

	def avaliable_cmds(self):
		return self.tasks.keys()

	def create_cmd(self, command):
		raise NoImplemented("not implemented, placeholder, tend to help user create cmds")

	def run(self):
		while True:
			# cmd is in json format
			# cmd = {
			#	network_type: "followers", # or friends
			#	user_id: id,
			#	data_type: 'id' # object
			#}
			cmd = self.get_cmd()

			if self.verbose:
				logger.info("new cmd: %s"%(cmd))

			command = cmd['cmd']

			#maybe change this to a map will be less expressive, and easier to read... but well, not too many cases here yet...
			if (command == 'TERMINATE'):
				break
			else:

				args = {
					"user_id": cmd['user_id'],
					"write_to_handlers": self.handlers
				}
				
				func = None
				if  (command == 'CRAWL_USER_TIMELINE'):
					func = getattr(self.user_api, self.tasks[command])
				elif (command in ['CRAWL_FRIENDS', 'CRAWL_FOLLOWERS']):
					data_type = cmd['data_type']
					func = getattr(self.user_api, self.tasks[command][data_type])
				
				if func:
					try:
						func(**args)
					except:
						logger.error("either the function you are calling doesn't exist, or you are calling the function with the wrong args!")
						pass
				else:
					logger.warn("whatever are you trying to do?")

		if self.verbose:
			logger.info("looks like i'm done...")
			for handler in self.handlers:
				logger.info(handler.stat())

			
		return True


			



			