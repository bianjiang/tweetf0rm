#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import logging

logger = logging.getLogger(__name__)

import multiprocessing as mp

import tweetf0rm.handler

MAX_QUEUE_SIZE = 32767 

class CrawlerProcess(mp.Process):

	def __init__(self, crawler_id, handlers = []):
		super(CrawlerProcess, self).__init__()
		self.crawler_id = crawler_id
		self.queue = mp.Queue(maxsize=MAX_QUEUE_SIZE)
		self.lock = mp.Lock()
		self.handlers = handlers
		logger.debug("number of handlers attached: %d"%(len(handlers)))


	def get_crawler_id(self):
		return self.crawler_id

	def enqueue(self, request):
		self.queue.put(request, block=True)
		return True

	def get_cmd(self):
		return  self.queue.get(block=True)


	def run(self):
		pass
			