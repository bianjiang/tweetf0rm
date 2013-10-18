#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.INFO)

import json
from tweetf0rm.utils import full_stack, hash_cmd, md5

def distribute_to(qsizes):
	'''
	return a list of keys (crawler_ids) that have the minimum number of pending cmds
	'''

	min_v = min(qsizes.values())

	return [crawler_id for crawler_id in qsizes if qsizes[crawler_id] == min_v]

class Scheduler(object):

	def __init__(self, node_id, config={}, proxies=[], verbose=False):
		self.node_id = node_id
		self.config = config

		if (len(proxies) > 0):
			self.proxy_dicts = proxy_checker(proxies)
			self.proxies = [proxy['http'] for proxy in self.proxy_dicts]

			# each process only get one apikey...  if there are more proxies than apikeys, each process can get more than one proxy that can be rotated when one fails. 
			number_of_processes = min(len(self.config['apikeys']), len(self.proxies))
		else:
			self.proxies = None
			number_of_processes = 1

		file_handler_config = {
			"name": "FileHandler",
			"args": {
				"verbose": verbose,
				"output_folder" : config["output"]
			}
		}

		crawlers = {}
		for idx in range(number_of_processes):
			crawler_id = md5('%s:%s'%(self.node_id, idx))
			crawler = UserRelationshipCrawler(crawler_id, copy.copy(apikeys), handlers=[create_handler(file_handler_config)], verbose=verbose, config=copy.copy(config))
			crawlers[crawler_id] = crawler
			crawler[crawler_id]['crawler'].start()

		self.crawlers = crawlers

	def is_alive(self):
		a = [1 if self.crawlers[crawler_id].is_alive() else 0 for crawler_id in self.crawlers]
		return sum(a) > 0

	# def distribute_to(self):
	# 	current_queue_size = 0
	# 	crawler = None
	# 	for idx in self.crawlers:
	# 		idx_queue_size = len(self.crawlers[idx]['queue'])
	# 		if (current_queue_size == 0 or current_queue_size > idx_queue_size):
	# 			current_queue_size = idx_queue_size
	# 			crawler = self.crawlers[idx]

	# 	return crawler

	def persist_queues(self):
		cmds = []
		for crawler_id in self.crawlers:
			cmds.extend(self.crawlers[crawler_id]['queue'])

		with open('__cmds.json', 'wb') as f:
			json.dump(cmds, f)

	def enqueue(self, cmd):

		if (cmd['cmd'] == 'TERMINATE'):
			[self.crawlers[idx].enqueue(cmd) for idx in self.crawlers]
		elif(cmd['cmd'] == 'CMD_FINISHED'):
			#acknowledged finished cmd 
			try:
				crawler_id = cmd['crawler_id']
				del self.crawlers[crawler_id]['queue'][cmd['cmd_hash']]
			except Exception as exc:
				logger.warn("the cmd doesn't exist? %s: %s"%(cmd['cmd_hash'], exc))
		else:
			crawler = distribute_to()

			self.crawlers[idx]['queue'][cmd['cmd_hash']] = hash_cmd(cmd)
			crawler.enqueue(cmd)

			if (self.verbose):
				logger.info("pusing [%s] to crawler: %d"%crawler.get_idx())


	def split(self, l, n):
		""" Yield successive n-sized chunks from l."""
		for i in xrange(0, len(l), n):
			yield l[i:i+n]

		