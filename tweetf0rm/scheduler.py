#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

import json, copy
from tweetf0rm.utils import full_stack, hash_cmd, md5
from tweetf0rm.proxies import proxy_checker
from process.user_relationship_crawler import UserRelationshipCrawler
#from handler.inmemory_handler import InMemoryHandler
from handler import create_handler
from tweetf0rm.redis_helper import NodeCoordinator

class Scheduler(object):

	def __init__(self, node_id, config={}, proxies=[], verbose=False):
		self.node_id = node_id
		self.config = config
		self.verbose = verbose
		if (len(proxies) > 0):
			
			self.proxy_list = proxy_checker(proxies)

			# each process only get one apikey...  if there are more proxies than apikeys, each process can get more than one proxy that can be rotated when one fails. 
			number_of_processes = min(len(self.config['apikeys']), len(self.proxy_list))
		else:
			self.proxy_list = None
			number_of_processes = 1

		if (verbose):
			logger.info("number of crawlers: %d"%(number_of_processes))

		file_handler_config = {
			"name": "FileHandler",
			"args": {
				"verbose": verbose,
				"output_folder" : config["output"]
			}
		}

		apikey_list = self.config['apikeys'].keys()

		crawlers = {}
		for idx in range(number_of_processes):
			crawler_id = md5('%s:%s'%(self.node_id, idx))
			apikeys = self.config['apikeys'][apikey_list[idx]]
			if (verbose):
				logger.info('creating a new crawler: %s'%crawler_id)
			crawler = UserRelationshipCrawler(self.node_id, crawler_id, copy.copy(apikeys), handlers=[create_handler(file_handler_config)], verbose=verbose, redis_config=copy.copy(config['redis_config']), proxies=self.proxy_list[idx]['proxy_dict'])
			crawlers[crawler_id] = {
				'crawler': crawler,
				'queue': {}
			}
			crawler.start()

		self.crawlers = crawlers
		self.node_coordinator = NodeCoordinator(config['redis_config'])
		self.node_coordinator.add_node(node_id)

	def is_alive(self):
		a = [1 if self.crawlers[crawler_id]['crawler'].is_alive() else 0 for crawler_id in self.crawlers]
		return sum(a) > 0

	def distribute_to(self):
		current_qsize = 0
		current_crawler_id = None
		for crawler_id in self.crawlers:
			qsize = len(self.crawlers[crawler_id]['queue'])
			if (current_qsize == 0 or current_qsize > qsize):
				current_qsize = qsize
				current_crawler_id = crawler_id

		return crawler_id

	def persist_queues(self):
		cmds = {}
		for crawler_id in self.crawlers:
			cmds.update(self.crawlers[crawler_id]['queue'])

		with open('__cmds.json', 'wb') as f:
			json.dump(cmds, f)

	def enqueue(self, cmd):

		if (cmd['cmd'] == 'TERMINATE'):
			[self.crawlers[crawler_id]['crawler'].enqueue(cmd) for crawler_id in self.crawlers]
		elif(cmd['cmd'] == 'CMD_FINISHED'):
			#acknowledged finished cmd 
			try:
				crawler_id = cmd['crawler_id']
				del self.crawlers[crawler_id]['queue'][cmd['cmd_hash']]
			except Exception as exc:
				logger.warn("the cmd doesn't exist? %s: %s"%(cmd['cmd_hash'], exc))
		else:
			crawler_id = self.distribute_to()

			self.crawlers[crawler_id]['queue'][hash_cmd(cmd)] = cmd
			self.crawlers[crawler_id]['crawler'].enqueue(cmd)

			if (self.verbose):
				logger.info("pusing [%s] to crawler: %s"%(hash_cmd(cmd), crawler_id))

	def check_local_qsizes(self):
		return {crawler_id:len(self.crawlers[crawler_id]['queue']) for crawler_id in self.crawlers}

		
	def split(self, l, n):
		""" Yield successive n-sized chunks from l."""
		for i in xrange(0, len(l), n):
			yield l[i:i+n]

		