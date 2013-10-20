#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

import sys, time, argparse
sys.path.append(".")

import multiprocessing as mp
from exceptions import InvalidConfig
from tweetf0rm.redis_helper import NodeQueue, NodeCoordinator
from tweetf0rm.utils import full_stack, node_id, public_ip
from tweetf0rm.proxies import proxy_checker
from tweetf0rm.scheduler import Scheduler

def check_config(config):
	if ('apikeys' not in config or 'redis_config' not in config):
		raise InvalidConfig("something is wrong with your config file... you have to have redis_config and apikeys")

def start_server(config, proxies):
	import copy
	
	check_config(config)
	config = copy.copy(config)

	this_node_id = node_id()
	node_queue = NodeQueue(this_node_id, redis_config=config['redis_config'])
	node_queue.clear()

	scheduler = Scheduler(this_node_id, config=config, proxies=proxies)

	logger.info('starting node_id: %s'%this_node_id)

	node_coordinator = NodeCoordinator(config['redis_config'])
	#time.sleep(5)
	# the main event loop, actually we don't need one, since we can just join on the crawlers and don't stop until a terminate command to each crawler, but we need one to check on redis command queue ...
	while True:
		# block, the main process...for a command
		if(not scheduler.is_alive()):
			logger.info("no crawler is alive... i'm done too...")
			break;

		cmd = node_queue.get(block=True, timeout=90)

		if cmd:
			scheduler.enqueue(cmd)

		logger.debug("cmd: %s"%cmd)
		logger.debug(node_coordinator.node_qsizes())
		logger.debug(scheduler.check_local_qsizes())

	# cmd = {
	# 	"cmd": "CRAWL_FRIENDS",
	# 	"user_id": 1948122342,
	# 	"data_type": "ids",
	# 	"depth": 2,
	# 	"bucket":"friend_ids"
	# }
	# cmd = {
	# 	"cmd": "CRAWL_FRIENDS",
	# 	"user_id": 1948122342,
	# 	"data_type": "users",
	# 	"depth": 2,
	# 	"bucket":"friends"
	# }
	# # cmd = {
	# # 	"cmd": "CRAWL_USER_TIMELINE",
	# # 	"user_id": 1948122342#53039176,
	##	"bucket": "timelines"
	# # }

	pass

if __name__=="__main__":
	import json, os
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', help="config.json that contains a) twitter api keys; b) redis connection string; c) mongodb connection string", required = True)
	parser.add_argument('-p', '--proxies', help="the crawler identifier; you can have multiple crawler accounts set in the config.json; pick one", required = True)

	args = parser.parse_args()

	with open(os.path.abspath(args.config), 'rb') as config_f, open(os.path.abspath(arg.proxies), 'rb') as proxy_f:
		config = json.load(config_f)
		proxies = json.load(proxy_f)

		start_server(config, proxies)