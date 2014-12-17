#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
# requests_log = logging.getLogger("requests")
# requests_log.setLevel(logging.WARNING)

import json, copy, time
from tweetf0rm.utils import full_stack, hash_cmd, md5, get_keys_by_min_value
from tweetf0rm.proxies import proxy_checker
from process.twitter_crawler import TwitterCrawler
#from handler.inmemory_handler import InMemoryHandler
from handler import create_handler
from tweetf0rm.redis_helper import NodeCoordinator, NodeQueue, CrawlerQueue
import twython, pprint
from operator import itemgetter

control_cmds = ['TERMINATE', 'CRAWLER_FLUSH', 'CRAWLER_FAILED']

class Scheduler(object):

	def __init__(self, node_id, config={}, proxies=[]):
		self.node_id = node_id
		self.config = config
		if (proxies and len(proxies) > 0):
			
			self.proxy_list = proxy_checker(proxies)

			logger.info("number of live proxies: %d"%(len(self.proxy_list)))

			# each process only get one apikey...  if there are more proxies than apikeys, each process can get more than one proxy that can be rotated when one fails. 
			number_of_processes = min(len(self.config['apikeys']), len(self.proxy_list))

			# if there are more proxies than apikeys, then each process will get a list of proxies, and the process will restart it self if a proxy failed, and try the next available proxy
			self.proxy_generator = self.split(self.proxy_list, number_of_processes)

		else:
			self.proxy_list = None
			self.proxy_generator = None
			number_of_processes = 1

		logger.info("number of crawlers: %d"%(number_of_processes))

		apikey_list = self.config['apikeys'].keys()


		self.crawlers = {}
		for idx in range(number_of_processes):
			try:
				self.new_crawler(self.node_id, self.config['apikeys'][apikey_list[idx]], config)
			except Exception as exc:
				logger.error(exc)
				pass


		self.node_coordinator = NodeCoordinator(config['redis_config'])
		self.node_coordinator.add_node(node_id)

		logger.info("number of crawlers: %d created"%(number_of_processes))

	def new_crawler(self, node_id, apikeys, config, crawler_proxies = None):
		file_handler_config = {
			"name": "FileHandler",
			"args": {
				"output_folder" : config["output"]
			}
		}

		crawler_id = apikeys['app_key']
		logger.debug('creating a new crawler: %s'%crawler_id)
		if (not crawler_proxies):
			crawler_proxies = next(self.proxy_generator) if self.proxy_generator else None

		crawler = TwitterCrawler(node_id, crawler_id, copy.copy(apikeys), handlers=[create_handler(file_handler_config)], redis_config=copy.copy(config['redis_config']), proxies=crawler_proxies)
		
		if (crawler_id in self.crawlers):
			#self.crawlers[crawler_id].clear()
			del self.crawlers[crawler_id]

		self.crawlers[crawler_id] = {
			'apikeys': apikeys,
			'crawler': crawler,
			'crawler_queue': CrawlerQueue(self.node_id, crawler_id, redis_config=copy.copy(config['redis_config'])),
			'crawler_proxies': crawler_proxies
		}
		crawler.start()



	def is_alive(self):
		a = [1 if self.crawlers[crawler_id]['crawler'].is_alive() else 0 for crawler_id in self.crawlers]
		return sum(a) > 0

	def crawler_status(self):
		status = []
		for crawler_id in self.crawlers:
			cc = self.crawlers[crawler_id]
			if ((not cc['crawler'].is_alive())): 
				
				if ('retry_timer_start_ts' in cc and (time.time() - cc['retry_timer_start_ts'] > 1800)):
					# retry 30 mins after the crawler dies... mostly the crawler died because "Twitter API returned a 503 (Service Unavailable), Over capacity"
					self.new_crawler(self.node_id, cc['apikeys'], self.config, cc['crawler_proxies'])
					cc = self.crawlers[crawler_id]
					logger.info('[%s] has been recrated...'%(crawler_id))
				else:
					if('retry_timer_start_ts' not in cc):
						cc['retry_timer_start_ts'] = int(time.time())
					else:
						logger.warn('[%s] failed; waiting to recreat in %f mins...'%(crawler_id, (time.time() + 1800 - cc['retry_timer_start_ts'])/float(60)))

			status.append({'crawler_id':crawler_id, 'alive?': cc['crawler'].is_alive(), 'qsize': cc['crawler_queue'].qsize(), 'crawler_queue_key': cc['crawler_queue'].get_key()})

		return status

	def balancing_load(self):
		'''
		Find the crawler that has the most load at this moment, and redistribut its item;
		Crawler is on a different subprocess, so we have to use redis to coordinate the redistribution...
		'''

		sorted_queues = self.sorted_local_queue(False)
		max_crawler_id, max_qsize = sorted_queues[-1]
		min_crawler_id, min_qsize = sorted_queues[0]
		logger.info("crawler with max_qsize: %s (%d)"%(max_crawler_id, max_qsize))
		logger.info("crawler with min_qsize: %s (%d)"%(min_crawler_id, min_qsize))
		logger.info("max_qsize - min_qsize > 0.5 * min_qsize ?: %r"%((max_qsize - min_qsize > 0.5 * min_qsize)))
		if (max_qsize - min_qsize > 0.5 * min_qsize):
			logger.info("load balancing process started...")
			cmds = []
			controls = []
			for i in range(int(0.3 * (max_qsize - min_qsize))):
				cmd = self.crawlers[max_crawler_id]['crawler_queue'].get()
				if (cmd['cmd'] in control_cmds):
					controls.append(cmd)
				else:
					cmds.append(cmd)

			# push control cmds back..
			for cmd in controls:
				self.crawlers[max_crawler_id]['crawler_queue'].put(cmd)

			logger.info("redistribute %d cmds"%len(cmds))
			for cmd in cmds:
				self.enqueue(cmd)

	def redistribute_crawler_queue(self, crawler_id):
		if (crawler_id in self.crawlers):
			logger.warn('%s just failed... redistributing its workload'%(crawler_id))
			try:
				self.node_coordinator.distribute_to_nodes(self.crawlers[crawler_id]['crawler_queue'])
				wait_timer = 180
				# wait until it dies (flushed all the data...)
				while(self.crawlers[crawler_id]['crawler'].is_alive() and wait_timer > 0):
					time.sleep(60)
					wait_timer -= 60

				self.crawlers[crawler_id]['retry_timer_start_ts'] = int(time.time())
			except Exception as exc:
				logger.error(full_stack())
		else:
			logger.warn("whatever are you trying to do? crawler_id: [%s] is not valid..."%(crawler_id))

	def enqueue(self, cmd):
		
		if (cmd['cmd'] == 'TERMINATE'):			
			[self.crawlers[crawler_id]['crawler_queue'].put(cmd) for crawler_id in self.crawlers]
		elif(cmd['cmd'] == 'CRAWLER_FLUSH'):
			[self.crawlers[crawler_id]['crawler_queue'].put(cmd) for crawler_id in self.crawlers]
		elif(cmd['cmd'] == 'BALANCING_LOAD'):
			self.balancing_load()
		elif(cmd['cmd'] == 'CRAWLER_FAILED'):
			crawler_id = cmd['crawler_id']
			self.redistribute_crawler_queue(crawler_id)
		else:
			'''distribute item to the local crawler that has the least tasks in queue'''
			for crawler_id, qsize in self.sorted_local_queue(False):
				if self.crawlers[crawler_id]['crawler'].is_alive():
					self.crawlers[crawler_id]['crawler_queue'].put(cmd)

					logger.debug("pushed %s to crawler: %s"%(cmd, crawler_id))
					break

	def check_crawler_qsizes(self):
		return {crawler_id:self.crawlers[crawler_id]['crawler_queue'].qsize() for crawler_id in self.crawlers}

	def sorted_local_queue(self, reverse=False):
		local_qsizes = self.check_crawler_qsizes()
		return sorted(local_qsizes.iteritems(), key=itemgetter(1), reverse=reverse)

	def split(self, lst, n):
		""" Yield successive n chunks of even sized sub-lists from lst."""
		lsize = {}
		results = {}
		for i in range(n):
			lsize[i] = 0
			results[i] = []

		
		for x in lst:
			idx = get_keys_by_min_value(lsize)[0]
			results[idx].append(x)
			lsize[idx] += 1

		for i in range(n):
			yield results[i]

		