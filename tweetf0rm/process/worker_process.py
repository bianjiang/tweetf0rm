#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

import multiprocessing as mp

import tweetf0rm.handler

MAX_QUEUE_SIZE = 32767 

class WorkerProcess(mp.Process):

	def __init__(self, handler_configs = [], verbose=False):
		super(WorkerProcess, self).__init__()
		self.queue = mp.Queue(maxsize=MAX_QUEUE_SIZE)
		self.lock = mp.Lock()
		self.verbose = verbose
		self.handlers = self.init_handlers(handler_configs)

	def init_handlers(self, handler_configs = []):
		handlers = []
		for handler_config in handler_configs:
			cls = getattr(tweetf0rm.handler, handler_config["name"])
			handlers.append(cls(**handler_config["args"]))
			logger.info("cls: %s"%cls)

		return handlers

	def enqueue(self, request):
		self.queue.put(request, block=True)
		return True

	def get_cmd(self):
		return  self.queue.get(block=True)


	def run(self):
		pass
			