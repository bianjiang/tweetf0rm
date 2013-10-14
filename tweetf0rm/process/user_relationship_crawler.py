#!/usr/bin/python
# -*- coding: utf-8 -*-
#

from .worker_process import WorkerProcess
from tweetf0rm.twitterapi.users import User
from tweetf0rm.exceptions import MissingArgs
import copy, json


class UserRelationshipCrawler(WorkerProcess):

	def __init__(self, apikeys, handlers = None):
		if (handlers == None):
			raise MissingArgs("you need a handler to write the data to...")
		super(UserRelationshipCrawler, self).__init__()
		self.apikeys = copy.copy(apikeys)
		self.handlers = handlers
		self.user_api = User(apikeys=apikeys, verbose=False)

	def start(self):
		while True:
			# cmd is in json format
			# cmd = {
			#	network_type: "followers", # or friends
			#	user_id: id,
			#	data_type: 'id' # object
			#}
			cmd = self.get_cmd()

			user_id = cmd['user_id']
			network_type = cmd['network_type']
			data_type = cmd['data_type']

			if (data_type == 'object' and network_type == 'friends'):
				self.user_api.find_all_friends(user_id=user_id, self.handlers)
			elif (data_type == 'object' and network_type == "followers"):
				self.user_api.find_all_followers(user_id=user_id, self.handlers)



			