#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
InMemoryHandler: handler that's collects the data in memory
'''

import logging

logger = logging.getLogger(__name__)

from .base_handler import BaseHandler

class InMemoryHandler(BaseHandler):
	'''
	inmemory_handler_config = {
		"name": "InMemoryHandler",
		"args": {
			"verbose": True
		}
	}
	inmemory_handler = create_handler(inmemory_handler_config) #InMemoryHandler(verbose=False, shared_buffer=d)
	'''

	def __init__(self, verbose=False):
		super(InMemoryHandler, self).__init__(verbose=verbose)
