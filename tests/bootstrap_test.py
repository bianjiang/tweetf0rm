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

	#@nottest
	def test_bootstrap(self):
		import tweetf0rm.bootstrap as bootstrap
		apikeys = self.config["apikeys"]["i0mf0rmer03"]
		bootstrap.start_server(apikeys) 
		# pass
		#from tweetf0rm.handler.inmemory_handler import InMemoryHandler
		#inmemory_handler = InMemoryHandler(verbose=False)


	@nottest
	def test_bootstrap_with_proxies(self):
		pass

	@nottest
	def test_proxy(self):
		import requests
		url = "http://google.com"
		headers = {
			'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0',
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'en-US,en;q=0.5'
		}

		for proxy in self.proxies['proxies']:
			try:			
				proxy_dict = {"http"  : 'http://%s'%proxy}

				r = requests.get(url, headers=headers, proxies=proxy_dict)
				if (r.status_code == requests.codes.ok):
					logger.info('GOOD: [%s] - %d'%(proxy, r.elapsed.seconds))
				else:
					logger.warn('BROKEN: [%s] - %d'%(proxy, r.elapsed.seconds))
			except:
				logger.warn('BROKEN: [%s] - %d'%(proxy, r.elapsed.seconds))
				pass


if __name__=="__main__":
	import nose
	#nose.main()
	result = nose.run()