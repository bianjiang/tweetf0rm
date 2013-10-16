#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Users.py: all user related farming; friends, followers, user objects; etc.
You can use this raw class, but normally you will use a script in the scripts folder
'''

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

import twython
import json, os, time
from tweetf0rm.exceptions import NotImplemented, MissingArgs, WrongArgs

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
			raise MissingArgs('apikeys is missing')

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

	def find_all_followers(self, user_id=None, write_to_handlers = None, bucket="followers"):

		if (not user_id):
			raise MissingArgs("user_id cannot be None")

		if (write_to_handlers == None):
			raise MissingArgs("come on, you gotta write the result to something...")

		cursor = -1
		while cursor != 0:
			try:
				followers = self.get_followers_list(user_id=user_id, cursor=cursor, count=200)

				for handler in write_to_handlers:
					handler.append(json.dumps(followers), bucket=bucket, key=user_id) 
					
				cursor = int(followers['next_cursor'])

				if self.verbose:
					logger.info("find #%d followers... NEXT_CURSOR: %d"%(len(followers["users"]), cursor))
				time.sleep(2)
			except twython.exceptions.TwythonRateLimitError:
				rate_limits = self.get_application_rate_limit_status(resources=['users', 'followers'])
				wait_for = int(rate_limits['resources']['followers']['/followers/list']['reset']) - time.time() + 10
				logger.info(rate_limits)
				logger.warn('rate time error, sleep for %d'%wait_for)
				if wait_for < 0:
					wait_for = 60

				time.sleep(wait_for)

		if self.verbose:
			logger.info("finished find_all_followers for %d..."%(user_id))
			# for handler in write_to_handlers:
			# 	#logger.info("appended %d items into [%s] with key [%s][%s]"%(len(handler.get("followers", user_id)), type(handler), "followers", user_id))
			# 	logger.info(handler.stat())


	def find_all_follower_ids(self, user_id=None, write_to_handlers = None, bucket = "follower_ids"):

		if (not user_id):
			raise MissingArgs("user_id cannot be None")

		if (write_to_handlers == None):
			raise MissingArgs("come on, you gotta write the result to something...")

		cursor = -1
		while cursor != 0:
			try:
				follower_ids = self.get_followers_ids(user_id=user_id, cursor=cursor, count=200)

				for handler in write_to_handlers:
					handler.append(json.dumps(follower_ids), bucket=bucket, key=user_id) 

				cursor = int(follower_ids['next_cursor'])

				if self.verbose:
					logger.info("find #%d followers... NEXT_CURSOR: %d"%(len(follower_ids["ids"]), cursor))
				time.sleep(2)
			except twython.exceptions.TwythonRateLimitError:
				rate_limits = self.get_application_rate_limit_status(resources=['users', 'followers'])
				wait_for = int(rate_limits['resources']['followers']['/followers/ids']['reset']) - time.time() + 10
				logger.info(rate_limits)
				logger.warn('rate time error, sleep for %d'%wait_for)
				if wait_for < 0:
					wait_for = 60

				time.sleep(wait_for)

		if self.verbose:
			logger.info("finished find_all_follower_ids for %d..."%(user_id))
			# for handler in write_to_handlers:
			# 	#logger.info("appended %d items into [%s] with key [%s][%s]"%(len(handler.get("follower_ids", user_id)), type(handler), "follower_ids", user_id))
			# 	logger.info(handler.stat())

	def find_all_friends(self, user_id=None, write_to_handlers=None, bucket="friends"):

		if (not user_id):
			raise MissingArgs("user_id cannot be None")

		if (write_to_handlers == None):
			raise MissingArgs("come on, you gotta write the result to something...")

		cursor = -1
		while cursor != 0:
			try:
				friends = self.get_friends_list(user_id=user_id, cursor=cursor, count=200)

				for handler in write_to_handlers:
					handler.append(json.dumps(friends), bucket=bucket, key=user_id) 


				cursor = int(friends['next_cursor'])

				if self.verbose:
					logger.info("find #%d friends... NEXT_CURSOR: %d"%(len(friends["users"]), cursor))

				time.sleep(2)
			except twython.exceptions.TwythonRateLimitError:
				rate_limits = self.get_application_rate_limit_status(resources=['users', 'friends'])
				wait_for = int(rate_limits['resources']['friends']['/friends/list']['reset']) - time.time() + 10
				logger.info(rate_limits)
				logger.warn('rate time error, sleep for %d'%wait_for)
				if wait_for < 0:
					wait_for = 60

				time.sleep(wait_for)

		if self.verbose:
			logger.info("finished find_all_friends for %d..."%(user_id))
			# for handler in write_to_handlers:
			# 	#logger.info("appended %d items into [%s] with key [%s][%s]"%(len(handler.get("friends", user_id)), type(handler), "friends", user_id))
			# 	logger.info(handler.stat())

	def find_all_friend_ids(self, user_id=None, write_to_handlers=None, bucket="friend_ids"):

		if (not user_id):
			raise MissingArgs("user_id cannot be None")

		if (write_to_handlers == None):
			raise MissingArgs("come on, you gotta write the result to something...")

		cursor = -1
		while cursor != 0:
			try:
				friend_ids = self.get_friends_ids(user_id=user_id, cursor=cursor, count=200)

				for handler in write_to_handlers:
					handler.append(json.dumps(friend_ids), bucket=bucket, key=user_id) 


				cursor = int(friend_ids['next_cursor'])

				if self.verbose:
					logger.info("find #%d friend_ids... NEXT_CURSOR: %d"%(len(friend_ids["ids"]), cursor))

				time.sleep(2)
			except twython.exceptions.TwythonRateLimitError:
				rate_limits = self.get_application_rate_limit_status(resources=['users', 'friends'])
				wait_for = int(rate_limits['resources']['friends']['/friends/ids']['reset']) - time.time() + 10
				logger.info(rate_limits)
				logger.warn('rate time error, sleep for %d'%wait_for)
				if wait_for < 0:
					wait_for = 60

				time.sleep(wait_for)

		if self.verbose:
			logger.info("finished find_all_friend_ids for %d..."%(user_id))
			# for handler in write_to_handlers:
			# 	#logger.info("appended %d items into [%s] with key [%s][%s]"%(len(handler.get("friend_ids", user_id)), type(handler), "friend_ids", user_id))
			# 	logger.info(handler.stat())

	def fetch_user_timeline(self, user_id = None, write_to_handlers=None, bucket="timelines"):

		if not user_id:
			raise Exception("user_timeline: user_id cannot be None")

		if (write_to_handlers == None):
			raise MissingArgs("come on, you gotta write the result to something...")

		prev_max_id = -1
		current_max_id = 0
		last_lowest_id = current_max_id # used to workaround users who has less than 200 tweets, 1 loop is enough...
		cnt = 0
		
		timeline = [] # holder tweets in memory... you won't get more than 3,200 tweets per user, so I guess this is fine...
		while current_max_id != prev_max_id:
			try:
				if current_max_id > 0:
					tweets = self.get_user_timeline(user_id=user_id, max_id=current_max_id, count=200)
				else:
					tweets = self.get_user_timeline(user_id=user_id, count=200)

				prev_max_id = current_max_id # if no new tweets are found, the prev_max_id will be the same as current_max_id

				for tweet in tweets:
					if current_max_id == 0 or current_max_id > int(tweet['id']):
						current_max_id = int(tweet['id'])

				#no new tweets found
				if (prev_max_id == current_max_id):
					break;

				timeline.extend(tweets)

				cnt += len(tweets)

				if self.verbose:
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

		for tweet in timeline:
			for handler in write_to_handlers:
				handler.append(json.dumps(tweet), bucket=bucket, key=user_id) 

		if self.verbose:
			logger.info("[%d] total tweets: %d "%(user_id, cnt))
			# for handler in write_to_handlers:
			# 	logger.info(handler.stat())
				


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


		