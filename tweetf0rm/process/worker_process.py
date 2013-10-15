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

	def __init__(self, handlers = [], verbose=False):
		super(WorkerProcess, self).__init__()
		self.queue = mp.Queue(maxsize=MAX_QUEUE_SIZE)
		self.lock = mp.Lock()
		self.verbose = verbose
		self.handlers = handlers
		logger.info(self.handlers)
		#self.handlers = self.init_handlers(handler_configs)

	

	def enqueue(self, request):
		self.queue.put(request, block=True)
		return True

	def get_cmd(self):
		return  self.queue.get(block=True)


	def run(self):
		pass
			