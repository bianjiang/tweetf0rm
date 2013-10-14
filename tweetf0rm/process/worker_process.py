#!/usr/bin/python
# -*- coding: utf-8 -*-
#

import multiprocessing as mp

class WorkerProcess(mp.Process):

	def __init__(self, queue, function, *args):
		super(WorkerProcess, self).__init__()
		self.queue = queue
		self.runtime_function = function
		self.runtime_function_args = * args

	def run(self):
		while True:
			