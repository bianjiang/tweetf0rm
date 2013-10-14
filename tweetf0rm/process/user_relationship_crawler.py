#!/usr/bin/python
# -*- coding: utf-8 -*-
#

from .worker_process import WorkerProcess
from tweetf0rm.twitterapi.users import User
import copy, json

class UserRelationshipCrawlerWorkerProcess):

	def __init__(self, apikeys, handlers = []):
		super(WorkerProcess, self).__init__()
		self.apikeys = copy.copy(apikeys)
		self.handlers = handlers
		self.user_api = User(apikeys=apikeys, verbose=False)

	def start(self):
		while True:
			cmd = self.get_cmd()