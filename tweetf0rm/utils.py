#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Singleton(type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

import requests, json, traceback, sys

def get_keys_by_min_value(qsizes):
	'''
	return a list of keys (crawler_ids) that have the minimum number of pending cmds
	'''

	min_v = min(qsizes.values())

	return [node_id for node_id in qsizes if qsizes[node_id] == min_v]
	
def full_stack():
	exc = sys.exc_info()[0]
	stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
	if not exc is None:  # i.e. if an exception is present
		del stack[-1]       # remove call of full_stack, the printed exception
							# will contain the caught exception caller instead
	trc = 'Traceback (most recent call last):\n'
	stackstr = trc + ''.join(traceback.format_list(stack))
	if not exc is None:
		 stackstr += '  ' + traceback.format_exc().lstrip(trc)
	return stackstr


def public_ip():
	r = requests.get('http://httpbin.org/ip')
	return r.json()['origin']

import hashlib
def md5(data):
	return hashlib.md5(data).hexdigest()

def hash_cmd(cmd):
	return md5(json.dumps(cmd))

def node_id():
	ip = public_ip()
	return md5(ip)
