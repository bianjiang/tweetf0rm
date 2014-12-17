#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Users.py: all user related farming; friends, followers, user objects; etc.
You can use this raw class, but normally you will use a script in the scripts folder
'''

import logging

logger = logging.getLogger(__name__)

import twython
import json, os, time
from tweetf0rm.exceptions import NotImplemented, MissingArgs, WrongArgs
from tweetf0rm.utils import md5

MAX_RETRY_CNT = 5
class TwitterAPI(twython.Twython):

	def __init__(self, *args, **kwargs):
		"""
		Constructor with apikeys, and output folder

		* apikeys: apikeys
		"""
		logger.info(kwargs)
		import copy

		apikeys = copy.copy(kwargs.pop('apikeys', None))
		
		if not apikeys:
			raise MissingArgs('apikeys is missing')

		self.apikeys = copy.copy(apikeys) # keep a copy
		#self.crawler_id = kwargs.pop('crawler_id', None)

		oauth2 = kwargs.pop('oauth2', True) # default to use oauth2 (application level access, read-only)

		if oauth2:
			apikeys.pop('oauth_token')
			apikeys.pop('oauth_token_secret')
			twitter = twython.Twython(apikeys['app_key'], apikeys['app_secret'], oauth_version=2)
			access_token = twitter.obtain_access_token()
			kwargs['access_token'] = access_token
			apikeys.pop('app_secret')
		
		kwargs.update(apikeys)

		super(TwitterAPI, self).__init__(*args, **kwargs)

		

	def rate_limit_error_occured(self, resource, api):
		rate_limits = self.get_application_rate_limit_status(resources=[resource])

		#e.g., ['resources']['followers']['/followers/list']['reset']

		wait_for = int(rate_limits['resources'][resource][api]['reset']) - time.time() + 10

		#logger.debug(rate_limits)
		logger.warn('[%s] rate limit reached, sleep for %d'%(rate_limits['rate_limit_context'], wait_for))
		if wait_for < 0:
			wait_for = 60

		time.sleep(wait_for)

	def find_all_followers(self, user_id=None, write_to_handlers = [], cmd_handlers=[], bucket="followers"):

		if (not user_id):
			raise MissingArgs("user_id cannot be None")

		retry_cnt = MAX_RETRY_CNT
		cursor = -1
		while cursor != 0 and retry_cnt > 1:
			try:
				followers = self.get_followers_list(user_id=user_id, cursor=cursor, count=200)

				for handler in write_to_handlers:
					handler.append(json.dumps(followers), bucket=bucket, key=user_id) 
				
				for handler in cmd_handlers:
					handler.append(json.dumps(followers), bucket=bucket, key=user_id) 

				cursor = int(followers['next_cursor'])
				
				logger.debug("find #%d followers... NEXT_CURSOR: %d"%(len(followers["users"]), cursor))
				time.sleep(2)
			except twython.exceptions.TwythonRateLimitError:
				self.rate_limit_error_occured('followers', '/followers/list')
			except Exception as exc:
				time.sleep(10)
				logger.debug("exception: %s"%exc)
				retry_cnt -= 1
				if (retry_cnt == 0):
					raise MaxRetryReached("max retry reached due to %s"%(exc))
				

		logger.debug("finished find_all_followers for %s..."%(user_id))


	def find_all_follower_ids(self, user_id=None, write_to_handlers = [], cmd_handlers=[], bucket = "follower_ids"):

		if (not user_id):
			raise MissingArgs("user_id cannot be None")

		retry_cnt = MAX_RETRY_CNT
		cursor = -1
		while cursor != 0 and retry_cnt > 1:
			try:
				follower_ids = self.get_followers_ids(user_id=user_id, cursor=cursor, count=200)

				for handler in write_to_handlers:
					handler.append(json.dumps(follower_ids), bucket=bucket, key=user_id)

				for handler in cmd_handlers:
					handler.append(json.dumps(follower_ids), bucket=bucket, key=user_id) 

				cursor = int(follower_ids['next_cursor'])

				logger.debug("find #%d followers... NEXT_CURSOR: %d"%(len(follower_ids["ids"]), cursor))
				time.sleep(2)
			except twython.exceptions.TwythonRateLimitError:
				self.rate_limit_error_occured('followers', '/followers/ids')
			except Exception as exc:
				time.sleep(10)
				logger.debug("exception: %s"%exc)
				retry_cnt -= 1
				if (retry_cnt == 0):
					raise MaxRetryReached("max retry reached due to %s"%(exc))


		logger.debug("finished find_all_follower_ids for %s..."%(user_id))


	def find_all_friends(self, user_id=None, write_to_handlers=[], cmd_handlers=[], bucket="friends"):

		if (not user_id):
			raise MissingArgs("user_id cannot be None")

		retry_cnt = MAX_RETRY_CNT
		cursor = -1
		while cursor != 0 and retry_cnt > 1:
			try:
				friends = self.get_friends_list(user_id=user_id, cursor=cursor, count=200)

				for handler in write_to_handlers:
					handler.append(json.dumps(friends), bucket=bucket, key=user_id)

				for handler in cmd_handlers:
					handler.append(json.dumps(friends), bucket=bucket, key=user_id) 

				cursor = int(friends['next_cursor'])

				logger.debug("find #%d friends... NEXT_CURSOR: %d"%(len(friends["users"]), cursor))

				time.sleep(2)
			except twython.exceptions.TwythonRateLimitError:
				self.rate_limit_error_occured('friends', '/friends/list')
			except Exception as exc:
				time.sleep(10)
				logger.debug("exception: %s"%exc)
				retry_cnt -= 1
				if (retry_cnt == 0):
					raise MaxRetryReached("max retry reached due to %s"%(exc))

		logger.debug("finished find_all_friends for %s..."%(user_id))


	def find_all_friend_ids(self, user_id=None, write_to_handlers=[], cmd_handlers=[], bucket="friend_ids"):

		if (not user_id):
			raise MissingArgs("user_id cannot be None")

		retry_cnt = MAX_RETRY_CNT
		cursor = -1
		while cursor != 0 and retry_cnt > 1:
			try:
				friend_ids = self.get_friends_ids(user_id=user_id, cursor=cursor, count=200)

				for handler in write_to_handlers:
					handler.append(json.dumps(friend_ids), bucket=bucket, key=user_id) 

				for handler in cmd_handlers:
					handler.append(json.dumps(friend_ids), bucket=bucket, key=user_id) 

				cursor = int(friend_ids['next_cursor'])

				logger.debug("find #%d friend_ids... NEXT_CURSOR: %d"%(len(friend_ids["ids"]), cursor))

				time.sleep(2)
			except twython.exceptions.TwythonRateLimitError:
				self.rate_limit_error_occured('friends', '/friends/ids')
			except Exception as exc:
				time.sleep(10)
				logger.debug("exception: %s"%exc)
				retry_cnt -= 1
				if (retry_cnt == 0):
					raise MaxRetryReached("max retry reached due to %s"%(exc))

		logger.debug("finished find_all_friend_ids for %s..."%(user_id))


	def fetch_user_timeline(self, user_id = None, write_to_handlers=[], cmd_handlers=[], bucket="timelines"):

		if not user_id:
			raise Exception("user_timeline: user_id cannot be None")


		prev_max_id = -1
		current_max_id = 0
		last_lowest_id = current_max_id # used to workaround users who has less than 200 tweets, 1 loop is enough...
		cnt = 0
		
		retry_cnt = MAX_RETRY_CNT
		timeline = [] # holder tweets in memory... you won't get more than 3,200 tweets per user, so I guess this is fine...
		while current_max_id != prev_max_id and retry_cnt > 1:
			try:
				if current_max_id > 0:
					tweets = self.get_user_timeline(user_id=user_id, max_id=current_max_id - 1, count=200)
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

				logger.debug('%d > %d ? %s'%(prev_max_id, current_max_id, bool(prev_max_id > current_max_id)))

				time.sleep(1)

			except twython.exceptions.TwythonRateLimitError:
				self.rate_limit_error_occured('statuses', '/statuses/user_timeline')
			except Exception as exc:
				time.sleep(10)
				logger.debug("exception: %s"%exc)
				retry_cnt -= 1
				if (retry_cnt == 0):
					raise MaxRetryReached("max retry reached due to %s"%(exc))

		if (len(timeline) > 0):
			for tweet in timeline:
				for handler in write_to_handlers:
					handler.append(json.dumps(tweet), bucket=bucket, key=user_id)

				for handler in cmd_handlers:
					handler.append(json.dumps(tweet), bucket=bucket, key=user_id)
		else:
			for handler in write_to_handlers:
				handler.append(json.dumps({}), bucket=bucket, key=user_id)

		logger.debug("[%s] total tweets: %d "%(user_id, cnt))	

	def fetch_tweet_by_id(self, tweet_id = None, write_to_handlers=[], cmd_handlers=[], bucket="tweets"):

		if not tweet_id:
			raise Exception("show_status: tweet_id cannot be None")

		tweet = None
		retry_cnt = MAX_RETRY_CNT
		while retry_cnt > 1:
			try:
				tweet = self.show_status(id=tweet_id)

				# logger.debug('%d > %d ? %s'%(prev_max_id, current_max_id, bool(prev_max_id > current_max_id)))
				logger.info("Fetched tweet [%s]" % (tweet_id))

				break

			except twython.exceptions.TwythonRateLimitError:
				self.rate_limit_error_occured('statuses', '/statuses/show')
			except twython.exceptions.TwythonError as te:
				if ( te.error_code == 404 or te.error_code == 403 ):
					logger.info("Tweet [%s] unavailable. Error code: %d" % (tweet_id, te.error_code))

					break
				else:
					time.sleep(10)
					logger.error("exception: %s"%(te))
					retry_cnt -= 1
					if (retry_cnt == 0):
						raise MaxRetryReached("max retry reached due to %s"%(te))
			except Exception as exc:
				time.sleep(10)
				logger.error("exception: %s, %s"%(exc, type(exc)))
				retry_cnt -= 1
				if (retry_cnt == 0):
					raise MaxRetryReached("max retry reached due to %s"%(exc))

		if (tweet != None):
			for handler in write_to_handlers:
				handler.append(json.dumps(tweet), bucket=bucket, key="tweetList")
		else:
			for handler in write_to_handlers:
				handler.append(json.dumps({"id":tweet_id}), bucket=bucket, key="tweetList")

		logger.debug("[%s] tweet fetched..." % tweet_id)


	def get_user_ids_by_screen_names(self, seeds):
		#get user id first
		screen_names = list(set(seeds))
		user_ids = set()		

		if len(screen_names) > 0:
			users = self.lookup_user(screen_name=screen_names)

			for user in users:
				user_ids.add(user['id'])

		return user_ids

	def get_users(self, seeds):
		#get user id first
		user_ids = list(set(seeds))
		users = set()
	

		if len(user_ids) > 0:
			users = self.lookup_user(user_id=user_ids)

		return users

	def search_by_query(self, query = None, geocode=None, lang=None, key=None, write_to_handlers=[], cmd_handlers=[], bucket="tweets"):

		if not query:
			raise Exception("search: query cannot be None")

		if not key:
			key = md5(query)

		logger.info("received query: %s "%(query))

		prev_max_id = -1
		current_max_id = 0
		last_lowest_id = current_max_id # used to workaround users who has less than 200 tweets, 1 loop is enough...
		cnt = 0
		
		retry_cnt = MAX_RETRY_CNT
		result_tweets = []
		while current_max_id != prev_max_id and retry_cnt > 1:
			try:
				if current_max_id > 0:
					tweets = self.search(q=query, geocode=geocode, lang=lang, max_id=current_max_id-1, count=100)
				else:
					tweets = self.search(q=query, geocode=geocode, lang=lang, count=100)


				prev_max_id = current_max_id # if no new tweets are found, the prev_max_id will be the same as current_max_id

				for tweet in tweets['statuses']:
					if current_max_id == 0 or current_max_id > long(tweet['id']):
						current_max_id = long(tweet['id'])

				#no new tweets found
				if (prev_max_id == current_max_id):
					break;

				result_tweets.extend(tweets['statuses'])

				cnt += len(tweets['statuses'])

				#logger.info(cnt)

				logger.debug('%d > %d ? %s'%(prev_max_id, current_max_id, bool(prev_max_id > current_max_id)))

				time.sleep(1)

			except twython.exceptions.TwythonRateLimitError:
				self.rate_limit_error_occured('search', '/search/tweets')
			except Exception as exc:
				time.sleep(10)
				logger.debug("exception: %s"%exc)
				retry_cnt -= 1
				if (retry_cnt == 0):
					raise MaxRetryReached("max retry reached due to %s"%(exc))

		if (len(result_tweets) > 0):
			for tweet in result_tweets:
				for handler in write_to_handlers:
					handler.append(json.dumps(tweet), bucket=bucket, key=key)

				for handler in cmd_handlers:
					handler.append(json.dumps(tweet), bucket=bucket, key=key)
		else:
			for handler in write_to_handlers:
				handler.append(json.dumps({}), bucket=bucket, key=key)

		logger.info("[%s] total tweets: %d "%(query, cnt))


		