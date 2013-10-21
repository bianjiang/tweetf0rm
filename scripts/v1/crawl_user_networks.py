#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

import argparse, pickle, os, json, sys, time

MAX_RETRY_CNT = 5

sys.path.append("..")
from tweetf0rmer.user_farm import UserFarm

def farm_user_network(apikeys=None, seeds= [], depth=3, output_folder='./user_network', network_type='followers'):

	output_folder = os.path.abspath('%s/%s'%(output_folder, network_type))
	user_farm = UserFarm(apikeys=apikeys, verbose=False, output_folder=output_folder)
	
	progress = {}
	try:
		with open('progress.pickle', 'rb') as pf:
			progress = pickle.load(pf)
	except:
		pass

	try:
		depth = max(progress.keys())

		logger.info('resume from depth: %d'%(depth))
	except:
		pass

	try:
		
		#get user id first
		user_ids = user_farm.get_user_ids(seeds)

		progress[depth] = user_ids

		logger.info("number of seeds: %d"%len(user_ids))

		while depth > 0 and len(user_ids) > 0:
			time.sleep(5)
			progress[depth-1] = set()

			while len(progress[depth]) > 0:

				user_id = progress[depth].pop()

				logger.info("fetching %s of %d"%(network_type, user_id))

				if os.path.exists(os.path.abspath('%s/%s'%(output_folder, user_id))):
					logger.info("%d already fetched... pass"%user_id)
					continue

				retry = False
				retry_cnt = MAX_RETRY_CNT
				while True:
					try:
						if network_type == 'friends':
							f_ids = user_farm.find_all_friends(user_id)
						else:
							f_ids = user_farm.find_all_followers(user_id)

						retry = False
						retry_cnt = MAX_RETRY_CNT
						if depth - 1 > 0:
							progress[depth-1].update(f_ids)
					except:
						retry = True
						retry_cnt -= 1
						time.sleep(60)
						logger.info("retries remaining if failed %d"%(retry_cnt))

					if not retry or retry_cnt == 0:
						break

				# retry failed
				if retry and retry_cnt == 0:
					# add unprocessed back to the queue
					progress[depth].add(user_id)

			logger.info('finish depth: %d'%(depth))

			depth -= 1

	except KeyboardInterrupt:
		print()
		logger.error('You pressed Ctrl+C!')
		raise
	except:		
		raise
	finally:
		user_farm.close()
		with open('progress.pickle', 'wb') as pf:
			pickle.dump(progress, pf)


if __name__=="__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--apikeys', help="config file for twitter api keys (json format); twitter requires you to have an account to crawl;", required = True)
	parser.add_argument('-c', '--crawler', help="the crawler identifier; you can have multiple crawler accounts set in the apikeys.json; pick one", required = True)
	parser.add_argument('-s', '--seeds', help="the config file for defining seed users and depth; see crawl_user_networks.json as an example", required = True)
	parser.add_argument('-o', '--output', help="define the location of the output", required = True)
	parser.add_argument('-nt', '--network_type', help='either [friends] or [followers]; default to farm followers', default='followers')
	args = parser.parse_args()
	
	with open(os.path.abspath(args.apikeys), 'rb') as apikeys_f, open(os.path.abspath(args.seeds), 'rb') as config_f:
		import json, os
		apikeys_config = json.load(apikeys_f)
		apikeys = apikeys_config.get(args.crawler, None)
		config = json.load(config_f)

		seeds = config['seeds'] if 'seeds' in config else []
		depth = int(config.get('depth', 3)) # by default only fetch 3 layers

		farm_user_network(apikeys, seeds, depth, args.output, args.network_type)
			


