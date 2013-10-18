#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from nose.tools import nottest

import sys, time
sys.path.append("..")

from tweetf0rm.redis_helper import NodeQueue
from tweetf0rm.utils import full_stack, node_id, public_ip

class TestClient:

	@classmethod
	def setup_class(cls):
		pass

	@classmethod
	def teardown_class(cls):
		pass

	def setup(self):
		import sys, os, json
		#sys.path.append("..")
		with open(os.path.abspath('config.json'), 'rb') as config_f:
			self.config = json.load(config_f)

	def teardown(self):
		pass


	def test_client(self):
		nid = node_id()
		logger.info("sending to %s"%(nid))
		node_queue = NodeQueue(nid, redis_config=self.config['redis_config'])
		#redis_cmd_queue.clear()

		# cmd = {
		# 	"cmd": "CRAWL_FRIENDS",
		# 	"user_id": 1948122342,
		# 	"data_type": "ids",
		# 	"depth": 1,
		# 	"bucket":"friend_ids"
		# }

		cmd = {
			"cmd": "CRAWL_USER_TIMELINE",
			"user_id": 1948122342,#53039176,
			"bucket": "timelines"
		}

		node_queue.put(cmd)

		cmd = {"cmd":"TERMINATE"}
		
		node_queue.put(cmd)

		return True


if __name__=="__main__":
	import nose
	#nose.main()
	result = nose.run()