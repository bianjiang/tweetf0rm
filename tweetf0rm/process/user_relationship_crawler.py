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

	def __init__(self, apikeys, handlers = None, verbose = False):
		if (handlers == None):
			raise MissingArgs("you need a handler to write the data to...")
		super(UserRelationshipCrawler, self).__init__()
		self.apikeys = copy.copy(apikeys)
		self.handlers = handlers
		self.verbose = verbose
		self.user_api = User(apikeys=apikeys, verbose=verbose)
		
		if (self.verbose):
			logger.info("# of handlers: %d"%(len(self.handlers)))

	def get_handlers(self):
		return self.handlers

	def avaliable_cmds(self):
		return ["TERMINATE", "CRAWL_FRIENDS", "CRAWL_FOLLOWERS"]

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

			if (command == 'TERMINATE'):
				break

			elif (command == 'CRAWL_FRIENDS'):
				user_id = cmd['user_id']
				data_type = cmd['data_type']
				if (data_type == 'object'):
					self.user_api.find_all_friends(user_id=user_id, write_to_handlers=self.handlers)
					for handler in self.get_handlers():
						logger.info(handler.stat())
				else:
					raise NoImplemented("%s not implemented"%(command, json.dumps(cmd)))
			elif (command == 'CRAWL_FOLLOWERS'):
				user_id = cmd['user_id']
				data_type = cmd['data_type']

				if (data_type == 'object'):
					self.user_api.find_all_followers(user_id=user_id, write_to_handlers=self.handlers)
				else:
					raise NoImplemented("%s not implemented"%(command, json.dumps(cmd)))
			else:
				raise NoImplemented("%s not implemented"%(command, json.dumps(cmd)))

		if self.verbose:
			logger.info("looks like i'm done...")
		return True


			



			