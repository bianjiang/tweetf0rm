#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.INFO)

import redis

class RedisHelper(object):

	def __init__(self, redis_config):
		self.redis_connection = redis.StrictRedis(host=redis_config['host'], port=redis_config['port'], db=0)
		self.password = redis_config['password']

	def __auth(self):
		self.redis_connection.execute_command("AUTH", self.password)
