#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
UserFarm.py: all user related farming; friends, followers, user objects; etc.
You can use this raw class, but normally you will use a script in the scripts folder
'''

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

import twython
import json, os, time

class User(twython.Twython):

	def __init__(self, *args, **kwargs):
		"""
		Constructor with apikeys, and output folder

		* verbose: be verbose about what we do. Defaults to False.
		* apikeys: apikeys
		"""
		import copy

		self.verbose = kwargs.pop('verbose', False)

		apikeys = copy.copy(kwargs.pop('apikeys', None))
		
		if not apikeys:
			raise Exception('apikeys is missing')

		self.apikeys = copy.copy(apikeys) # keep a copy

		oauth2 = kwargs.pop('oauth2', True) # default to use oauth2 (application level access, read-only)

		if oauth2:
			apikeys.pop('oauth_token')
			apikeys.pop('oauth_token_secret')
			twitter = twython.Twython(apikeys['app_key'], apikeys['app_secret'], oauth_version=2)
			access_token = twitter.obtain_access_token()
			kwargs['access_token'] = access_token
			apikeys.pop('app_secret')
		
		kwargs.update(apikeys)

		super(User, self).__init__(*args, **kwargs)

	def find_all_followers(self, user_id=None, write_to_handler = None):

		if not user_id:
			raise Exception("find_all_friend_ids: user_id cannot be None")

		if write_to_handler == None:
			raise Exception("come on, you gotta write the result to something...")


		follower_ids = []

		cursor = -1
		while cursor != 0:
			try:
				followers = self.get_followers_list(user_id=user_id, cursor=cursor)
				
				for follower in followers['users']:
					follower_ids.append(follower['id'])

				self.write_to_handler.append(json.dumps(followers), key=user_id)
				cursor = int(followers['next_cursor'])
				time.sleep(5)
			except twython.exceptions.TwythonRateLimitError:
				rate_limits = self.get_application_rate_limit_status(resources=['users', 'followers'])
				wait_for = int(rate_limits['resources']['followers']['/followers/list']['reset']) - time.time() + 10
				logger.info(rate_limits)
				logger.warn('rate time error, sleep for %d'%wait_for)
				if wait_for < 0:
					wait_for = 60

				time.sleep(wait_for)

		follower_ids = set(follower_ids)
		logger.info("found %d followers..."%(len(follower_ids)))
		return follower_ids


	def find_all_friends(self, user_id=None, write_to_handler=None):

		if not user_id:
			raise Exception("find_all_friend_ids: user_id cannot be None")

		if write_to_handler == None:
			write_to_handler = self.write_to_handler

		friend_ids = []
		cursor = -1
		while cursor != 0:
			try:
				friends = self.get_friends_list(user_id=user_id, cursor=cursor)

				for friend in friends['users']:
					friend_ids.append(friend['id'])

				self.write_to_handler.append(json.dumps(friends), key=user_id)
				cursor = int(friends['next_cursor'])
				time.sleep(5)
			except twython.exceptions.TwythonRateLimitError:
				rate_limits = self.get_application_rate_limit_status(resources=['users', 'friends'])
				wait_for = int(rate_limits['resources']['friends']['/friends/list']['reset']) - time.time() + 10
				logger.info(rate_limits)
				logger.warn('rate time error, sleep for %d'%wait_for)
				if wait_for < 0:
					wait_for = 60

				time.sleep(wait_for)

		friend_ids = set(friend_ids)
		logger.info("found %d friends..."%(len(friend_ids)))
		return friend_ids

	def user_timeline(self, user_id = None, write_to_handler=None):

		if not user_id:
			raise Exception("user_timeline: user_id cannot be None")

		if write_to_handler == None:
			write_to_handler = self.write_to_handler

		prev_max_id = -1
		current_max_id = 0

		cnt = 0
		
		while current_max_id != prev_max_id:
			try:
				if current_max_id > 0:
					tweets = self.get_user_timeline(user_id=user_id, max_id=current_max_id, count=200)
				else:
					tweets = self.get_user_timeline(user_id=user_id, count=200)

				prev_max_id = current_max_id # if no new tweets are found, the prev_max_id will be the same as current_max_id

				for tweet in tweets:
					write_to_handler.append(json.dumps(tweet), key=user_id)

					if current_max_id == 0 or current_max_id > int(tweet['id']):
						current_max_id = int(tweet['id'])

				cnt += len(tweets)
				logger.debug('%d > %d ? %s'%(prev_max_id, current_max_id, bool(prev_max_id > current_max_id)))
				logger.info("fetched tweets: %d"%cnt)
				time.sleep(1)
			except twython.exceptions.TwythonRateLimitError:
				rate_limits = self.get_application_rate_limit_status(resources=['statuses'])
				wait_for = int(rate_limits['resources']['statuses']['/statuses/user_timeline']['reset']) - time.time() + 10
				logger.info(rate_limits)
				logger.warn('rate time error, sleep for %d'%wait_for)
				if wait_for < 0:
					wait_for = 60

				time.sleep(wait_for)

		logger.info("[%d] total tweets: %d "%(user_id, cnt))

	def get_user_ids(self, seeds):
		#get user id first
		screen_names = []
		user_ids = set()
		for each in seeds:
			try:
				user_id = int(each)
				user_ids.add(user_id)
			except:
				screen_names.append(each)

		if len(screen_names) > 0:
			users = self.lookup_user(screen_name=screen_names)

			for user in users:
				user_ids.add(user['id'])

		return user_ids


		