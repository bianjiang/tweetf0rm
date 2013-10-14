#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
file_handler.py: handler that's collects the data, and write to the disk on a separate thread; 

'''

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

import time, os, sys, threading, time

class FileHandler(object):

	def __init__(self, output_folder, buffer_size=1024 * 1024, verbose=False):

		import futures, os
		self.output_folder = os.path.abspath(output_folder)
		if not os.path.exists(self.output_folder):
			os.makedirs(self.output_folder)

		self.executor = futures.ThreadPoolExecutor(max_workers=1)
		self.buffer = {}
		self.buffer_size = buffer_size
		self.verbose = verbose
		self.last_rolling_timestamp = 0
		self.cnt = 0
		self.lock = threading.Lock()

	def append(self, data, key='current_timestampe'):

		self.lock.acquire()
		if key not in self.buffer:
			self.buffer[key] = []

		self.buffer[key].append(data)

		csize = sys.getsizeof(self.buffer[key])

		self.lock.release()

		# in memory buffer size, doesn't mean the file size... 
		if csize > self.buffer_size:
			self.flush(key)

	def flush(self, key):

		import copy
		items = copy.copy(self.buffer[key])

		del self.buffer[key][:]
		del self.buffer[key]

		future = self.executor.submit(self.__write_to, key, items)

		return future

	def close(self):		
		logger.info("waiting for existing data to be flushed... be patient... this will be quick")
		time.sleep(10) # sleep for 10 secs, it's possible that the feed hasn't ended, so new data are still being appended... 
		self.lock.acquire()
		keys = self.buffer.keys()
		for k in keys:
			future = self.flush(k)
			future.result()

		self.lock.release()

	# sometime if the process restarts, we need to delete a partial finished file and restart from a clean state
	def delete(self, key):
		filename = os.path.abspath('%s/%s'%(self.output_folder, key))
		try:
			os.remove(filename)
		except:
			pass


	def __write_to(self, key, items):
		current = time.gmtime()

		if key == 'current_timestampe':
			key = int(time.mktime(current))

		filename = os.path.abspath('%s/%s'%(self.output_folder, key))

		with open(filename, 'ab+') as f:
			for line in items:
				f.write('%s\n'%line)
		
			if self.verbose:
				logger.info("flushed %d to %s"%(len(items), filename))

		return True

	