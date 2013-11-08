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
from process.user_relationship_crawler import UserRelationshipCrawler
#from handler.inmemory_handler import InMemoryHandler
from handler import create_handler
from tweetf0rm.redis_helper import NodeCoordinator, NodeQueue
import twython, pprint


class Scheduler(object):

	def __init__(self, node_id, config={}, proxies=[]):
		self.node_id = node_id
		self.config = config
		if (len(proxies) > 0):
			
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
				self.new_crawler(self.config['apikeys'][apikey_list[idx]], config)
			except:
				pass

		self.node_coordinator = NodeCoordinator(config['redis_config'])
		self.node_coordinator.add_node(node_id)

		logger.info("number of crawlers: %d created"%(number_of_processes))

	def new_crawler(self, apikeys, config, crawler_proxies = None):
		file_handler_config = {
			"name": "FileHandler",
			"args": {
				"output_folder" : config["output"]
			}
		}

		try:
			#crawler_id = md5('%s:%s'%(self.node_id, idx))
			#apikeys = self.config['apikeys'][apikey_list[idx]]
			crawler_id = apikeys['app_key']
			logger.debug('creating a new crawler: %s'%crawler_id)
			if (not crawler_proxies):
				crawler_proxies = next(self.proxy_generator) if self.proxy_generator else None

			crawler = UserRelationshipCrawler(self.node_id, crawler_id, copy.copy(apikeys), handlers=[create_handler(file_handler_config)], redis_config=copy.copy(config['redis_config']), proxies=crawler_proxies)
			
			if (crawler_id in self.crawlers):
				del self.crawlers[crawler_id]

			self.crawlers[crawler_id] = {
				'apikeys': apikeys,
				'crawler': crawler,
				'queue': {},
				'crawler_proxies': crawler_proxies
			}
			crawler.start()
		except twython.exceptions.TwythonAuthError as exc:
			logger.error('%s: %s'%(exc, apikeys))
		except:
			raise


	def is_alive(self):
		a = [1 if self.crawlers[crawler_id]['crawler'].is_alive() else 0 for crawler_id in self.crawlers]
		return sum(a) > 0

	def crawler_status(self):
		status = []
		for crawler_id in self.crawlers:
			cc = self.crawlers[crawler_id]
			if ((not cc['crawler'].is_alive()) and time.time() - cc['retry_timer_start_ts'] > 1800): # retry 30 mins after the crawler dies... mostly the crawler died because "Twitter API returned a 503 (Service Unavailable), Over capacity"
				self.new_crawler(cc['apikeys'], self.config, cc['crawler_proxies'])

			status.append({crawler_id: cc['crawler'].is_alive(), 'qsize': len(cc['queue'])})

		return status

		#return [{crawler_id: True, 'qsize': len(self.crawlers[crawler_id]['queue'])}  else {crawler_id: False}  for crawler_id in self.crawlers]

	def distribute_to(self):
		current_qsize = None
		current_crawler_id = None
		for crawler_id in self.crawlers:
			qsize = len(self.crawlers[crawler_id]['queue'])

			if (current_qsize == None or current_qsize >= qsize):
				current_qsize = qsize
				current_crawler_id = crawler_id
				#logger.info('%s:%d >= %d?'%(crawler_id, current_qsize, qsize))


		return current_crawler_id

	def persist_queues(self):
		cmds = {}
		for crawler_id in self.crawlers:
			cmds.update(self.crawlers[crawler_id]['queue'])

		with open('%s_queued_cmds.json'%(int(time.time())), 'wb') as f:
			json.dump(cmds, f)

	def remaining_tasks(self):
		qsizes = [len(self.crawlers[crawler_id]['queue']) for crawler_id in self.crawlers]
		return sum(qsizes)


	def enqueue(self, cmd):

		if (cmd['cmd'] == 'TERMINATE'):
			# note that we need to save both the queues that are local, but also let others know that i am dead, and I need to have my redis queue cleared out... (it's possible that another node is still trying to send data into my redis queue, after i am dead... this needs to be handled as maintenance job (take the cmds in dead nodes' queue, and persist...))
			if (remaining_tasks > 0):
				self.persist_queues()
			[self.crawlers[crawler_id]['crawler'].enqueue(cmd) for crawler_id in self.crawlers]
		elif(cmd['cmd'] == 'CRAWLER_FLUSH'):
			[self.crawlers[crawler_id]['crawler'].enqueue(cmd) for crawler_id in self.crawlers]
		elif(cmd['cmd'] == 'CRAWLER_FAILED'):
			crawler_id = cmd['crawler_id']
			if (crawler_id in self.crawlers):
				logger.warn('%s just failed... redistributing its workload'%(crawler_id))
				try:
					self.node_coordinator.distribute_to_nodes(self.crawlers[crawler_id]['queue'])
					wait_timer = 180
					# wait until it dies (flushed all the data...)
					while(self.crawlers[crawler_id]['crawler'].is_alive() && wait_timer > 0):
						time.sleep(60)
						wait_timer -= 60

					self.crawlers[crawler_id]['retry_timer_start_ts'] = int(time.time())
				except Exception as exc:
					logger.error(full_stack())
			else:
				logger.warn("whatever are you trying to do? crawler_id: [%s] is not valid..."%(crawler_id))
		elif(cmd['cmd'] == 'CMD_FINISHED'):
			#acknowledged finished cmd 
			try:
				crawler_id = cmd['crawler_id']
				del self.crawlers[crawler_id]['queue'][cmd['cmd_hash']]
				logger.debug('removed cmd: %s from [%s]'%(cmd['cmd_hash'], crawler_id))
			except Exception as exc:
				logger.warn("the cmd doesn't exist? %s: %s"%(cmd['cmd_hash'], exc))
		else:
			crawler_id = self.distribute_to()
			cmd_hash = hash_cmd(cmd)
			cmd['cmd_hash'] = cmd_hash
			self.crawlers[crawler_id]['queue'][cmd_hash] = cmd

			self.crawlers[crawler_id]['crawler'].enqueue(cmd)

			logger.debug("pushed %s: [%s] to crawler: %s"%(cmd, cmd_hash, crawler_id))

	def check_local_qsizes(self):
		#logger.info(self.crawlers)
		return {crawler_id:len(self.crawlers[crawler_id]['queue']) for crawler_id in self.crawlers}


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

		