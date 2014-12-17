#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.DEBUG)

from nose.tools import nottest

import sys, os, json, exceptions
sys.path.append("..")

from tweetf0rm.utils import full_stack
from tweetf0rm.proxies import proxy_checker

import multiprocessing as mp

from tweetf0rm.twitterapi.twitter_api import TwitterAPI

class Handler(object):

	def append(self,data, bucket=None, key=None):
		logger.info(data)
		pass

def call_user_api(apikeys, client_args):

	twitter_api = TwitterAPI(apikeys=apikeys, client_args=client_args)
	twitter_api.find_all_friend_ids(53039176, [Handler()])

			
class TestTwitterRateLimit:

	@classmethod
	def setup_class(cls):
		pass

	@classmethod
	def teardown_class(cls):
		pass

	def setup(self):
		import sys, os, json
		#sys.path.append("..")
		with open(os.path.abspath('rate_limit_test.json'), 'rb') as config_f, open(os.path.abspath('proxy.json'), 'rb') as proxy_f:
			self.config = json.load(config_f)
			self.proxies = json.load(proxy_f)

	def teardown(self):
		pass

	@nottest
	def test_china_proxy(self):
		apikeys = self.config['apikeys']['i0mf0rmer13']
			
		client_args = {
			"timeout": 300,
			"proxies": {'http':'203.156.207.249:8080'}#proxy_list[i]['proxy_dict']
		}

		call_user_api(apikeys, client_args)


	@nottest
	def test_rate_limit(self):
		from tweetf0rm.proxies import proxy_checker

		proxy_list = proxy_checker(self.proxies['proxies'])

		ps = []
		for i, twitter_user in enumerate(self.config['apikeys']):
			apikeys = self.config['apikeys'][twitter_user]
			

			client_args = {
				"timeout": 300,
				"proxies": {'http':'203.156.207.249:8080'}#proxy_list[i]['proxy_dict']
			}
			logger.info(client_args)

			p = mp.Process(target=call_user_api, args=(apikeys, client_args, ))
			ps.append(p)
			p.start()

		for p in ps:
			p.join()

if __name__=="__main__":
	import nose
	#nose.main()
	result = nose.run(TestTwitterRateLimit)