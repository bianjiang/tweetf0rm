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

	def __init__(self, idx, handlers = [], verbose=False, config=None):
		super(WorkerProcess, self).__init__()
		self.idx = idx
		self.queue = mp.Queue(maxsize=MAX_QUEUE_SIZE)
		self.lock = mp.Lock()
		self.verbose = verbose
		self.handlers = handlers
		self.config = config
		if verbose:
			logger.info("number of handlers attached: %d"%(len(handlers)))
		#logger.info(self.handlers)
		#self.handlers = self.init_handlers(handler_configs)

	def get_idx(self):
		return self.idx

	def enqueue(self, request):
		self.queue.put(request, block=True)
		return True

	def get_cmd(self):
		return  self.queue.get(block=True)


	def run(self):
		pass
			