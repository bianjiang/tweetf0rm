#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from nose.tools import nottest

import sys, time, argparse, random
sys.path.append(".")
from tweetf0rm.redis_helper import NodeQueue
from tweetf0rm.utils import node_id, public_ip

def cmd(config):
	nid = node_id()
	logger.info("sending to %s"%(nid))
	node_queue = NodeQueue(nid, redis_config=config['redis_config'])
	#redis_cmd_queue.clear()

	cmd = {
		"cmd": "CRAWL_FRIENDS",
		"user_id": 1948122342, #1948122342, #random.uniform(1, 10),#1948122342,
		"data_type": "ids",
		"depth": 1,
		"bucket":"friend_ids"
	}

	# cmd = {
	# 	"cmd": "CRAWL_USER_TIMELINE",
	# 	"user_id": 1948122342,#53039176,
	# 	"bucket": "timelines"
	# }

	node_queue.put(cmd)

if __name__=="__main__":
	import json, os
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', help="config.json that contains a) twitter api keys; b) redis connection string; c) mongodb connection string", required = True)

	args = parser.parse_args()

	with open(os.path.abspath(args.config), 'rb') as config_f:
		config = json.load(config_f)

		cmd(config)