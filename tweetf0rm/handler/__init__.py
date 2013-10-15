
from inmemory_handler import InMemoryHandler
from file_handler import FileHandler
__all__ = ["InMemoryHandler", "FileHandler"]

import copy
avaliable_handlers = copy.copy(__all__)

import tweetf0rm.handler

def create_handler(handler_config=None):
	# inmemory_handler_config = {
	# 	"name": "InMemoryHandler",
	# 	"args": {
	# 		"verbose": True
	# 	}
	# }
	cls = getattr(tweetf0rm.handler, handler_config["name"])
	return cls(**handler_config["args"])

def create_handlers(handler_configs=None):
	handlers = []
	for handler_config in handler_configs:		
		handlers.append(create_handler(handler_config))
	return handlers
