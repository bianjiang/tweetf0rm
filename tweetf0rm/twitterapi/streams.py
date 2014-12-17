#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
stream.py: 

KeywordsStreamer: straightforward class that tracks a list of keywords; most of the jobs are done by TwythonStreamer; the only thing this is just attach a WriteToHandler so results will be saved

'''

import logging

logger = logging.getLogger(__name__)

from twython import TwythonStreamer
import os, copy, datetime, json

class Streamer(TwythonStreamer):

	def __init__(self, *args, **kwargs):
		"""
		Constructor with apikeys, and output folder

		* apikeys: apikeys
		"""
		logger.info(kwargs)
		import copy

		apikeys = copy.copy(kwargs.pop('apikeys', None))
		
		if not apikeys:
			raise MissingArgs('apikeys is missing')

		self.apikeys = copy.copy(apikeys) # keep a copy
		
		kwargs.update(apikeys)

		super(Streamer, self).__init__(*args, **kwargs)


	def on_success(self, data):
		if 'text' in data:
			self.counter += 1
			if self.counter % 1000 == 0:
				logger.info("received: %d"%self.counter)
			#logger.debug(data['text'].encode('utf-8'))
			self.write_to_handler.append(json.dumps(data))

			
	def on_error(self, status_code, data):
		 logger.warn(status_code)

		
	def close(self):
		self.disconnect()
		self.write_to_handler.close()
		