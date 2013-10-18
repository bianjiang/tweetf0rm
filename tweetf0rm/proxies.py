#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

from tweetf0rm.utils import full_stack
import requests, futures

def check_proxy(proxy, timeout):
	url = "http://google.com"
	headers = {
		'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0',
		'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate',
		'Accept-Language': 'en-US,en;q=0.5'
	}

	p = {'proxy':proxy,'proxy_dict':{"http"  : 'http://%s'%proxy}}

	r = requests.get(url, headers=headers, proxies=p['proxy_dict'], timeout=timeout)

	try:
		if (r.status_code == requests.codes.ok):
			return True, p
		else:
			return False, None
	except:
		return False, None

def proxy_checker(proxies):
	proxies = set(proxies)

	logger.info('%d proxies to check'%(len(proxies)))
	good_proxies = []

	with futures.ThreadPoolExecutor(max_workers=10) as executor:

		future_to_proxy = {executor.submit(check_proxy, proxy, 60): proxy for proxy in proxies}
			
		for future in futures.as_completed(future_to_proxy):

			proxy = future_to_proxy[future]
			try:
				good, proxy_dict = future.result()
			except Exception as exc:
				logger.info('%r generated an exception: %s'%(proxy, exc))
			else:
				if (good):
					good_proxies.append(proxy_dict)

		return good_proxies





