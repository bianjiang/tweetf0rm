#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s-[%(asctime)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

import sys, time, argparse, json, os, pprint
sys.path.append(".")

import multiprocessing as mp
from tweetf0rm.exceptions import InvalidConfig
from tweetf0rm.redis_helper import NodeQueue, NodeCoordinator
from tweetf0rm.utils import full_stack, node_id, public_ip
from tweetf0rm.proxies import proxy_checker
from tweetf0rm.scheduler import Scheduler
import time, os, tarfile

def check_config(config):
	if ('apikeys' not in config or 'redis_config' not in config):
		raise InvalidConfig("something is wrong with your config file... you have to have redis_config and apikeys")

def tarball_results(data_folder, bucket, output_tarball_foldler, timestamp):

	data_folder = os.path.join(os.path.abspath(data_folder), bucket)

	if (not os.path.exists(data_folder)):
		os.makedirs(data_folder)

	output_tarball_foldler = os.path.join(os.path.abspath(output_tarball_foldler), bucket)

	if (not os.path.exists(output_tarball_foldler)):
		os.makedirs(output_tarball_foldler)

	gz_file = os.path.join(output_tarball_foldler, '%s.tar.gz'%timestamp) 
	ll = []
	
	for root, dirs, files in os.walk(data_folder):
		if (len(files) > 0):
			with tarfile.open(gz_file, "w:gz") as tar:
				cnt = 0
				for f in files:
					f_abspath = os.path.join(root, f)
					(mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(f_abspath)

					if (mtime <= timestamp):
						tar.add(f_abspath, '%s/%s'%(timestamp,f), recursive=False)
						ll.append(f_abspath)
						cnt += 1
						if (cnt % 1000 == 0):
							logger.info("processed %d files"%(cnt))
					else:
						pass
				#logger.debug(time.ctime(atime))


				tar.close()

				for f in ll:

					os.remove(f)

				return True, gz_file

	return False, gz_file
			#tar.add()
def start_server(config, proxies):
	import copy
	
	check_config(config)
	config = copy.copy(config)

	folders_to_create = []
	buckets = ["tweets", "followers", "follower_ids", "friends", "friend_ids", "timelines"]

	ouput_folder = os.path.abspath(config['output'])
	archive_output = os.path.abspath(config['archive_output']) if config['archive_output'] else ouput_folder
	archive_output = os.path.join(archive_output, 'archived')

	folders_to_create.append(ouput_folder)
	folders_to_create.append(archive_output)

	for bucket in buckets:
		folders_to_create.append(os.path.join(ouput_folder, bucket))
		folders_to_create.append(os.path.join(archive_output, bucket))

	for folder_to_create in folders_to_create:
		if (not os.path.exists(folder_to_create)):
			os.makedirs(folder_to_create)

	this_node_id = node_id()
	node_queue = NodeQueue(this_node_id, redis_config=config['redis_config'])
	node_queue.clear()

	scheduler = Scheduler(this_node_id, config=config, proxies=proxies)

	logger.info('starting node_id: %s'%this_node_id)

	node_coordinator = NodeCoordinator(config['redis_config'])
	#time.sleep(5)
	# the main event loop, actually we don't need one, since we can just join on the crawlers and don't stop until a terminate command to each crawler, but we need one to check on redis command queue ...
	
	last_archive_ts = time.time() + 3600 # the first archive event starts 2 hrs later... 
	pre_time = time.time()
	while True:
		# block, the main process...for a command
		if(not scheduler.is_alive()):
			logger.info("no crawler is alive... i'm done too...")
			break;

		cmd = node_queue.get(block=True, timeout=360)

		if cmd:
			scheduler.enqueue(cmd)
		
		if (time.time() - pre_time > 120):
			logger.info(pprint.pformat(scheduler.crawler_status()))
			#logger.info('local queue_sizes: %s'%scheduler.check_local_qsizes())
			pre_time = time.time()
			cmd = {'cmd': 'CRAWLER_FLUSH'}
			scheduler.enqueue(cmd)

		if (time.time() - last_archive_ts > 3600):
			with futures.ProcessPoolExecutor(max_workers=1) as executor:

				for bucket in ["tweets", "followers", "follower_ids", "friends", "friend_ids", "timelines"]:
					future = executor.submit(tarball_results, ouput_folder, bucket, archive_output, time.time() - 3600)

					future.add_done_callback(lambda f: logger.info("archive %s created? %s"%f.result()))
				

	# cmd = {
	# 	"cmd": "CRAWL_FRIENDS",
	# 	"user_id": 1948122342,
	# 	"data_type": "ids",
	# 	"depth": 2,
	# 	"bucket":"friend_ids"
	# }
	# cmd = {
	# 	"cmd": "CRAWL_FRIENDS",
	# 	"user_id": 1948122342,
	# 	"data_type": "users",
	# 	"depth": 2,
	# 	"bucket":"friends"
	# }
	# # cmd = {
	# # 	"cmd": "CRAWL_USER_TIMELINE",
	# # 	"user_id": 1948122342#53039176,
	##	"bucket": "timelines"
	# # }


if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--config', help="config.json that contains a) twitter api keys; b) redis connection string;", required = True)
	parser.add_argument('-p', '--proxies', help="the proxies.json file")

	args = parser.parse_args()

	proxies = None
	if args.proxies:
		with open(os.path.abspath(args.proxies), 'rb') as proxy_f:
			proxies = json.load(proxy_f)['proxies']

	with open(os.path.abspath(args.config), 'rb') as config_f:
		config = json.load(config_f)	
		
		try:
			start_server(config, proxies)
		except KeyboardInterrupt:
			print()
			logger.error('You pressed Ctrl+C!')
			pass
		except Exception as exc:		
			logger.error(exc)
			logger.error(full_stack())
		finally:
			pass