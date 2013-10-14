#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

import argparse, pickle, os, json, sys, time
sys.path.append("..")
from tweetf0rmer.user_farm import UserFarm
from tweetf0rmer.utils import full_stack

# there isn't much try and fail done yet
def farm_user_timelines(apikeys, seeds, output_folder):

	user_farm = UserFarm(apikeys=apikeys, verbose=False, output_folder=os.path.abspath(output_folder))

	try:
		#get user id first
		user_ids = user_farm.get_user_ids(seeds)

		for user_id in user_ids:
			# current it skips the user if the result file is already there. Obviously this is not reliable since the error could raise when only half of the tweets for an user is finished... this will mean losing the other half for this user... but my current use case doesn't really care... since I have millions of users to worry about, losing one isn't that big of deal... but certainly needs a better way to track progress
			if not os.path.exists(os.path.abspath('%s/%s'%(output_folder, user_id))):
				user_farm.user_timeline(user_id)
	except KeyboardInterrupt:
		logger.warn('You pressed Ctrl+C!')
		raise
	except:		
		raise
	finally:
		user_farm.close()

if __name__=="__main__":
	

	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--apikeys', help="config file for twitter api key (json format)", required = True)
	parser.add_argument('-c', '--crawler', help="the crawler identifier; you can have multiple crawler accounts set in the apikeys.json; pick one", required = True)
	parser.add_argument('-s', '--seeds', help="the list of users you want to crawl their timelines; see crawl_user_timelines.json as an example", required = True)
	parser.add_argument('-o', '--output', help="define the location of the output (each user's timeline will be in its own file under this output folder identified by the user id", required = True)
	args = parser.parse_args()
	
	with open(os.path.abspath(args.apikeys), 'rb') as apikeys_f, open(os.path.abspath(args.seeds), 'rb') as config_f:
		import json, os
		apikeys_config = json.load(apikeys_f)
		apikeys = apikeys_config.get(args.crawler, None)
		config = json.load(config_f)

		seeds = config['seeds'] if 'seeds' in config else []
		
		while True:				
			try:
				farm_user_timelines(apikeys, seeds, args.output)
			except KeyboardInterrupt:
				logger.warn('You pressed Ctrl+C!')
				sys.exit(0)
			except:
				logger.error(full_stack())
				logger.info('failed, retry')
				time.sleep(10)
		
			


