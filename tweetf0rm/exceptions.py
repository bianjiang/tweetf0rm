#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author: ji0ng.bi0n


class NotImplemented(Exception):
	pass

class MissingArgs(Exception):
	pass

class WrongArgs(Exception):
	pass

class InvalidConfig(Exception):
	pass

class MaxRetryReached(Exception):
	pass