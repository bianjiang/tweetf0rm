#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s-[%(asctime)s][%(module)s][%(funcName)s][%(lineno)d]: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

import argparse, pickle, os, json, sys, time
sys.path.append("..")


from tweetf0rm.proxies import proxy_checker

if __name__=="__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('-p', '--proxies', help="define the location of the output;", default="proxies.json")
	args = parser.parse_args()
	
	with open(os.path.abspath(args.proxies), 'rb') as proxy_f:
		proxies = json.load(proxy_f)['proxies']
		
		proxies = [proxy['proxy'] for proxy in proxy_checker(proxies)]

		logger.info('%d live proxies left'%(len(proxies)))

		with open(os.path.abspath(args.proxies), 'wb') as proxy_f:
			json.dump({'proxies':proxies}, proxy_f)
	

			


