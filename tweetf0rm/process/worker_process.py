#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import multiprocessing as mp

MAX_QUEUE_SIZE = 32767 

class WorkerProcess(mp.Process):

	def __init__(self):
		super(WorkerProcess, self).__init__()
		self.queue = mp.Queue(maxsize=MAX_QUEUE_SIZE)

	def enqueue(self, request):
		self.queue.put(request, block=True)
		return True

	def get_cmd(self):
		cmd_string = self.queue.get(block=True)

		return json.loads(cmd)

	def start(self):
		pass
			