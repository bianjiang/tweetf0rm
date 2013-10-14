
from inmemory_handler import InMemoryHandler
from file_handler import FileHandler
__all__ = ["InMemoryHandler", "FileHandler"]

import copy
avaliable_handlers = copy.copy(__all__)