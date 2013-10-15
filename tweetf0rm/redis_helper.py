#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.INFO)

import redis

def redis_pub():
	# these will return nothing since user_relationship_crawler works on a different process
	# for handler in user_relationship_crawler.get_handlers():
	# 	logger.info(handler.stat())

	#r = redis.StrictRedis(host='localhost', port=6379, db=0)

	#r.execute_command("AUTH", "wh0tever")
	#r.set('node_id', node_id())
	#logger.info(r.get('node_id'))
	#logger.info(node_id())