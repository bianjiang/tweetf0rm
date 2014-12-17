#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

from nose.tools import nottest

import sys, os, json, exceptions, time
sys.path.append("..")

from tweetf0rm.utils import full_stack, hash_cmd, md5, get_keys_by_min_value
from tweetf0rm.proxies import proxy_checker
from tweetf0rm.redis_helper import NodeCoordinator, NodeQueue

class TestBootstrap:

	@classmethod
	def setup_class(cls):
		pass

	@classmethod
	def teardown_class(cls):
		pass

	def setup(self):
		import sys, os, json
		#sys.path.append("..")
		with open(os.path.abspath('../config.json'), 'rb') as config_f, open(os.path.abspath('proxies.json'), 'rb') as proxy_f:
			self.config = json.load(config_f)
			self.proxies = json.load(proxy_f)

	def teardown(self):
		pass

	#@nottest
	def test_search(self):
		from tweetf0rm.twitterapi.twitter_api import TwitterAPI
		from tweetf0rm.handler.inmemory_handler import InMemoryHandler

		apikeys = self.config["apikeys"]["i0mf0rmer03"]
		
		#inmemoryhandler = InMemoryHandler()
		twitter_api = TwitterAPI(apikeys=apikeys)
		tweets = twitter_api.search_by_query(query="transmasculine OR transman OR transmale")
		#tweets = twitter_api.search(q="twitter", geocode=None, lang=None, count=100)
		logger.info(tweets)


	@nottest
	def test_distribute_to_local(self):
		def distribute_to(crawlers):

			current_qsize = None
			current_crawler_id = None
			for crawler_id in crawlers:
				qsize = len(crawlers[crawler_id]['queue'])
				if (current_qsize == None or current_qsize >= qsize):
					current_qsize = qsize
					current_crawler_id = crawler_id

			return current_crawler_id

		crawlers = {}

		crawlers[1] = {'queue': {1:'',2:'',3:'',4:'',5:''}}
		crawlers[2] = {'queue': {1:'',2:''}}
		crawlers[3]= {'queue': {1:'',2:'', 3:''}}

		for i in range(10, 20):
			crawler_id = distribute_to(crawlers)
			crawlers[crawler_id]['queue'][i] = ''

		logger.info(crawlers)

	@nottest
	def test_distribute_to(self):
		def distribute_to(qsizes):
			'''
			return a list of keys (crawler_ids) that have the minimum number of pending cmds
			'''

			min_v = min(qsizes.values())

			return [crawler_id for crawler_id in qsizes if qsizes[crawler_id] == min_v]

		qsizes = {
			"1": 5,
			"2": 5,
			"3": 2
			}

		for i in range(10):
			c_id = distribute_to(qsizes)[0]
			
			qsizes[c_id] += 1

		logger.info(qsizes)

	@nottest
	def test_get_user_id(self):
		from tweetf0rm.twitterapi.twitter_api import TwitterAPI
		from tweetf0rm.handler.inmemory_handler import InMemoryHandler

		apikeys = self.config["apikeys"]["i0mf0rmer03"]
		
		#inmemoryhandler = InMemoryHandler()
		twitter_api = TwitterAPI(apikeys=apikeys)
		userIds = twitter_api.get_user_ids_by_screen_names(["AmericanCance"])
		logger.info(userIds)

	@nottest
	def test_bootstrap(self):
		import tweetf0rm.bootstrap as bootstrap
		#apikeys = self.config["apikeys"]["i0mf0rmer03"]
		bootstrap.start_server(self.config, self.proxies["proxies"]) 
		# pass
		#from tweetf0rm.handler.inmemory_handler import InMemoryHandler
		#inmemory_handler = InMemoryHandler(verbose=False)

	@nottest
	def test_redis_connections(self):
		nodes = {}

		cnt = 0
		while True:
			nodes[cnt] = NodeQueue("node_id", redis_config=self.config['redis_config'])
			cnt += 1
			if (cnt % 5 == 0):
				nodes.clear()
			time.sleep(1)

	@nottest
	def test_split(self):

		def split(lst, n):
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

			


		l = range(150)

		# logger.info({}.values())
		# n = iter(l)
		# logger.info(next(n))
		# logger.info(next(n))
		# logger.info(next(n))
		# logger.info(next(n))
		# logger.info(next(n))
		# logger.info(next(n))
		# try:
		# 	logger.info(next(n))
		# except Exception as exc:
		# 	try:
		# 		logger.info(type(exc))
		# 		logger.info(isinstance(exc, exceptions.StopIteration))
		# 		raise
		# 	except Exception as sss:
		# 		logger.info("again...%r"%(exc))
		# 		raise
			#raise
		p = split(l, 16)
		for i in range(16):
			logger.info(len(next(p)))
		# pp = next(p) if p else None
		# logger.info(pp)


		#logger.info(next(p))

	@nottest
	def test_proxy(self):
		proxies = proxy_checker(self.proxies['proxies'])
		#logger.info(proxies)
		logger.info('%d good proxies left'%len(proxies))

		# ps = []
		# for d in proxies:
		#  	ps.append(d['proxy'])

		# with open(os.path.abspath('proxy.json'), 'wb') as proxy_f:
		#  	json.dump({'proxies':ps}, proxy_f)

if __name__=="__main__":
	import nose
	#nose.main()
	result = nose.run(TestBootstrap)