#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.INFO)

class Scheduler(object):

	def __init__(self, config={}, proxies=[]):
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
				"verbose": True,
				"output_folder" : "./data"
			}
		}

		crawlers = []
		for i in range(number_of_processes):
			crawlers.append(UserRelationshipCrawler(copy.copy(apikeys), handlers=[create_handler(file_handler_config)], verbose=verbose, config=copy.copy(config)))

		r = [crawler.start() for crawler in crawlers]

		self.crawlers = crawlers


	def split(self, l, n):
		""" Yield successive n-sized chunks from l."""
		for i in xrange(0, len(l), n):
			yield l[i:i+n]

		