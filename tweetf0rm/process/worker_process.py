#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import multiprocessing as mp

MAX_QUEUE_SIZE = 32767 

class WorkerProcess(mp.Process):

	def __init__(self):
		super(WorkerProcess, self).__init__()
		self.queue = mp.Queue(maxsize=MAX_QUEUE_SIZE)
		self.lock = mp.Lock()

	def enqueue(self, request):
		self.queue.put(request, block=True)
		return True

	def get_cmd(self):
		return  self.queue.get(block=True)


	def start(self):
		pass
			