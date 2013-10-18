#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

import time

import multiprocessing as mp
from exceptions import InvalidConfig
from tweetf0rm.redis_helper import NodeQueue
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
	#apikeys = copy.copy(config['apikeys'])
	verbose = bool(config['verbose']) if config['verbose'] else False

	this_node_id = node_id()
	node_queue = NodeQueue(this_node_id, redis_config=config['redis_config'])
	node_queue.clear()

	scheduler = Scheduler(this_node_id, config=config, proxies=proxies, verbose=verbose)

	if (verbose):
		logger.info('starting node_id: %s'%this_node_id)

	#time.sleep(5)
	# the main event loop, actually we don't need one, since we can just join on the crawlers and don't stop until a terminate command to each crawler, but we need one to check on redis command queue ...
	while True:
		# block, the main process...for a command
		logger.info("waiting for cmd...")
		if(not scheduler.is_alive()):
			logger.info("no crawler is alive... i'm done too...")
			break;

		cmd = node_queue.get(block=True, timeout=5)

		if cmd:
			scheduler.enqueue(cmd)

		if (verbose):
			logger.info("cmd: %s"%cmd)


		

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

	# user_relationship_crawler.enqueue(cmd)
	#user_relationship_crawler.enqueue({"cmd":"TERMINATE"})

	# user_relationship_crawler.join()

	# these will return nothing since user_relationship_crawler works on a different process
	# for handler in user_relationship_crawler.get_handlers():
	# 	logger.info(handler.stat())

	#r = redis.StrictRedis(host='localhost', port=6379, db=0)

	#r.execute_command("AUTH", "wh0tever")
	#r.set('node_id', node_id())
	#logger.info(r.get('node_id'))
	#logger.info(node_id())
	pass

if __name__=="__main__":
	bootstrap()
	quit()
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', help="config.json that contains a) twitter api keys; b) redis connection string; c) mongodb connection string", required = True)
	parser.add_argument('-c', '--crawler', help="the crawler identifier; you can have multiple crawler accounts set in the config.json; pick one", required = True)

	args = parser.parse_args()

	with open(os.path.abspath(args.config), 'rb') as config_f:
		import json, os
		start_server()