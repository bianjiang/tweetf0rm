#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from process.user_relationship_crawler import UserRelationshipCrawler
#from process.user_timeline_crawler import UserTimelineProcessCrawler
from handler.inmemory_handler import InMemoryHandler
from handler import create_handler
import multiprocessing as mp
from exceptions import InvalidConfig
from tweetf0rm.redis_helper import RedisQueue
from tweetf0rm.utils import full_stack
import time
def check_config(config, crawler):
	if ('apikeys' not in config or crawler not in config['apikeys'] or 'redis_config' not in config):
		raise InvalidConfig("something is wrong with your config file... you have to have redis_config, apikeys, and crawler name specified... ")

def start_server(config, crawler):
	import copy
	from utils import node_id, public_ip
	logger.info(public_ip())
	check_config(config, crawler)
	config = copy.copy(config)
	apikeys = copy.copy(config['apikeys'][crawler])

	redis_cmd_queue = RedisQueue(name="cmd", redis_config=config['redis_config'])
	redis_cmd_queue.clear()

	inmemory_handler_config = {
		"name": "InMemoryHandler",
		"args": {
			"verbose": True
		}
	}

	inmemory_handler = create_handler(inmemory_handler_config) #InMemoryHandler(verbose=False, shared_buffer=d)

	user_relationship_crawler = UserRelationshipCrawler(copy.copy(apikeys), handlers=[inmemory_handler], verbose=True, config=config)

	user_relationship_crawler.start()

	# the main event loop, actually we don't need one, since we can just join on the crawlers and don't stop until a terminate command to each crawler, but we need one to check on redis command queue ...
	while True:
		# block, the main process...for a command
		logger.info("waiting for cmd...")
		if(not user_relationship_crawler.is_alive()):
			logger.info("no crawler is alive... i'm done too...")
			break;

		cmd = redis_cmd_queue.get(block=True, timeout=5)

		logger.info(cmd)
		if cmd:
			user_relationship_crawler.enqueue(cmd)

		

	# cmd = {
	# 	"cmd": "CRAWL_FRIENDS",
	# 	"user_id": 1948122342,
	# 	"data_type": "ids",
	# 	"depth": 2,
	# 	"result_bucket":"friend_ids"
	# }
	# cmd = {
	# 	"cmd": "CRAWL_FRIENDS",
	# 	"user_id": 1948122342,
	# 	"data_type": "users",
	# 	"depth": 2,
	# 	"result_bucket":"friends"
	# }
	# # cmd = {
	# # 	"cmd": "CRAWL_USER_TIMELINE",
	# # 	"user_id": 1948122342#53039176
	# # }

	# user_relationship_crawler.enqueue(cmd)
	#user_relationship_crawler.enqueue({"cmd":"TERMINATE"})

	user_relationship_crawler.join()

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