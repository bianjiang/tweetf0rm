#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

#import redis
from process.user_relationship_crawler import UserRelationshipCrawler
#from process.user_timeline_crawler import UserTimelineProcessCrawler
from handler.inmemory_handler import InMemoryHandler

def start_server(apikeys):
	import copy
	from utils import node_id, public_ip
	logger.info(public_ip())

	inmemoryhandler = InMemoryHandler()
	user_relationship_crawler = UserRelationshipCrawler(copy.copy(apikeys), [inmemoryhandler])

	cmd = {
		user_id: 1,
		network_type: "friends",
		data_type: "object"
	}
	user_relationship_crawler.enqueue(cmd)
	
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