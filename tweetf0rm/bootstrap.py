#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

#import redis
from process.user_relationship_crawler import UserRelationshipCrawler
#from process.user_timeline_crawler import UserTimelineProcessCrawler
from handler.inmemory_handler import InMemoryHandler
import multiprocessing as mp

def start_server(apikeys):
	import copy
	from utils import node_id, public_ip
	logger.info(public_ip())

	#manager = mp.Manager()

	#handlers = manager.list()
	#handlers.append(InMemoryHandler(verbose=True))
	inmemory_handler_config = {
		"name": "InMemoryHandler",
		"args": {
			"verbose": True
		}
	}
	logger.info(inmemory_handler_config)
	user_relationship_crawler = UserRelationshipCrawler(copy.copy(apikeys), [inmemory_handler_config], verbose=True)

	user_relationship_crawler.start()

	# cmd = {
	# 	"cmd": "CRAWL_FRIENDS",
	# 	"user_id": 1948122342,
	# 	"data_type": "id"
	# }
	cmd = {
		"cmd": "CRAWL_USER_TIMELINE",
		"user_id": 53039176
	}

	user_relationship_crawler.enqueue(cmd)
	user_relationship_crawler.enqueue({"cmd":"TERMINATE"})

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