#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
InMemoryHandler: handler that's collects the data in memory
'''

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

from .base_handler import BaseHandler

class InMemoryHandler(BaseHandler):

	def __init__(self, verbose=False):
		super(InMemoryHandler, self).__init__(verbose=verbose)

