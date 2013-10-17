#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.INFO)

from nose.tools import nottest

import sys
sys.path.append("..")

from tweetf0rm.redis_helper import RedisQueue
from tweetf0rm.utils import full_stack

from tweetf0rm.proxies import proxy_checker

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
		with open(os.path.abspath('config.json'), 'rb') as config_f, open(os.path.abspath('proxy.json'), 'rb') as proxy_f:
			self.config = json.load(config_f)
			self.proxies = json.load(proxy_f)

	def teardown(self):
		pass


	@nottest
	def test_get_user_id(self):
		from tweetf0rm.twitterapi.users import User
		from tweetf0rm.handler.inmemory_handler import InMemoryHandler

		apikeys = self.config["apikeys"]["i0mf0rmer03"]
		
		#inmemoryhandler = InMemoryHandler()
		user_api = User(apikeys=apikeys)
		userIds = user_api.get_user_ids(["FDA_Drug_Info"])
		logger.info(userIds)

	@nottest
	def test_bootstrap(self):
		import tweetf0rm.bootstrap as bootstrap
		#apikeys = self.config["apikeys"]["i0mf0rmer03"]
		bootstrap.start_server(self.config, self.proxies) 
		# pass
		#from tweetf0rm.handler.inmemory_handler import InMemoryHandler
		#inmemory_handler = InMemoryHandler(verbose=False)


	@nottest
	def test_bootstrap_with_proxies(self):
		pass

	@nottest
	def test_proxy(self):
		proxies = proxy_checker(self.proxies['proxies'])

		logger.info('%d good proxies left'%len(proxies))

		ps = []
		for d in proxies:
			ps.append(d['http'])

		with open(os.path.abspath('proxy.json'), 'rb') as proxy_f:
			josn.dump({'proxies':ps}, proxy_f)

if __name__=="__main__":
	import nose
	#nose.main()
	result = nose.run(TestBootstrap)