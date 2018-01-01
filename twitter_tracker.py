    #!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.handlers

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='(%(asctime)s) [%(process)d] %(levelname)s: %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

import sys
import os
import time
import json
import util
import itertools
from twitter_crawler import TwitterCrawler

WAIT_TIME = 30
CLIENT_ARGS = {"timeout": 30}

def flash_cmd_config(cmd_config, cmd_config_filepath, output_folder):

    with open(os.path.abspath(cmd_config_filepath), 'w') as cmd_config_wf:
        json.dump(cmd_config, cmd_config_wf)

    with open(os.path.abspath('%s/%s'%(output_folder, os.path.basename(cmd_config_filepath))), 'w') as cmd_config_wf:
        json.dump(cmd_config, cmd_config_wf)

def collect_tweets_by_search_terms(search_configs_filepath, output_folder, config):
    
    apikeys = list(config['apikeys'].values()).pop()

    search_configs = {}
    with open(os.path.abspath(search_configs_filepath), 'r') as search_configs_rf:
        search_configs = json.load(search_configs_rf)

    for search_config_id in itertools.cycle(search_configs):
       
        search_config = search_configs[search_config_id]

        search_terms = [term.lower() for term in search_config['terms']]
        querystring = '%s'%(' OR '.join('(' + term + ')' for term in search_terms))
        since_id = search_config['since_id'] if 'since_id' in search_config else 0
        geocode = tuple(search_config['geocode']) if ('geocode' in search_config and search_config['geocode']) else None

        logger.info('REQUEST -> (md5(querystring): [%s]; since_id: [%d]; geocode: [%s])'%(util.md5(querystring.encode('utf-8')), since_id, geocode))


        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder = output_folder)
            since_id = twitterCralwer.search_by_query(querystring, geocode = geocode, since_id = since_id)
        except Exception as exc:
            logger.error(exc)
            logger.error(util.full_stack())
            pass

        search_config['since_id'] = since_id
        search_config['querystring'] = querystring
        search_config['geocode'] = geocode

        search_configs[search_config_id] = search_config

        flash_cmd_config(search_configs, search_configs_filepath, output_folder)

        logger.info('COMPLETED -> (md5(querystring): [%s]; since_id: [%d]; geocode: [%s])'%(util.md5(querystring.encode('utf-8')), since_id, geocode))
        logger.info('PAUSE %ds to CONTINUE...'%WAIT_TIME)
        time.sleep(WAIT_TIME)

def collect_tweets_by_ids(tweet_ids_config_filepath, output_folder, config):

    apikeys = list(config['apikeys'].values()).pop()

    tweet_ids_config = {}
    with open(os.path.abspath(tweet_ids_config_filepath), 'r') as tweet_ids_config_rf:
        tweet_ids_config = json.load(tweet_ids_config_rf)

    max_range = 100
    
    current_ix = tweet_ids_config['current_ix'] if ('current_ix' in tweet_ids_config) else 0
    total = len(tweet_ids_config['tweet_ids'][current_ix:])
    tweet_id_chuncks = util.chunks(tweet_ids_config['tweet_ids'][current_ix:], max_range)

    for tweet_ids in tweet_id_chuncks:
        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder = output_folder)
            twitterCralwer.lookup_tweets_by_ids(tweet_ids)
            current_ix += len(tweet_ids)

        except Exception as exc:
            logger.error(exc)
            logger.error(util.full_stack()) #don't care, if Ctrl+c is hit, does not handle it.  When you restart, it restarts from the last chunk (too much trouble to handle Ctrl + c).
            # you will get duplicate tweets, so what...
            pass

        tweet_ids_config['current_ix'] = current_ix
        
        flash_cmd_config(tweet_ids_config, tweet_ids_config_filepath, output_folder)

        logger.info('COMPLETED -> (current_ix: [%d/%d])'%(current_ix, total))
        logger.info('PAUSE %ds to CONTINUE...'%WAIT_TIME)
        time.sleep(WAIT_TIME)
    else:
        logger.info('[tweets_by_ids] ALL COMPLETED')

def collect_tweets_by_id_range(tweet_id_range_config_filepath, output_folder, config):

    apikeys = list(config['apikeys'].values()).pop()

    tweet_ids_config = {}
    with open(os.path.abspath(tweet_id_range_config_filepath), 'r') as tweet_id_range_config_rf:
        tweet_id_range_config = json.load(tweet_id_range_config_rf)

    max_range = 100
    current_id = tweet_id_range_config['current_id'] if ('current_id' in tweet_id_range_config) else 0
    end_id = tweet_id_range_config['end_id'] if ('end_id' in tweet_id_range_config) else 0

    tweet_id_chuncks = util.chunks(range(current_id, end_id), max_range)

    for tweet_ids in tweet_id_chuncks:

        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder = output_folder)
            twitterCralwer.lookup_tweets_by_ids(tweet_ids)
            current_id += len(tweet_ids)
        except Exception as exc:
            logger.error(exc)
            logger.error(util.full_stack()) #don't care, if Ctrl+c is hit, does not handle it.  When you restart, it restarts from the last chunk (too much trouble to handle Ctrl + c).
            # you will get duplicate tweets, so what...
            pass

        tweet_id_range_config['current_id'] = current_id
        
        flash_cmd_config(tweet_id_range_config, tweet_id_range_config_filepath, output_folder)

        logger.info('COMPLETED -> (current_id/end_id: [%d/%d])'%(current_id, end_id))
        logger.info('PAUSE %ds to CONTINUE...'%WAIT_TIME)
        time.sleep(WAIT_TIME)
    else:
        logger.info('[tweets_by_id_range] ALL COMPLETED')

def collect_users(call, users_config_filepath, output_folder, config):

    apikeys = list(config['apikeys'].values()).pop()

    users_config = {}
    with open(os.path.abspath(users_config_filepath), 'r') as users_config_rf:
        users_config = json.load(users_config_rf)

    max_range = 100
    current_ix = users_config['current_ix'] if ('current_ix' in users_config) else 0
    total = len(users_config['users'][current_ix:])
    user_chuncks = util.chunks(users_config['users'][current_ix:], max_range)

    for users in user_chuncks:
        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder = output_folder)
            twitterCralwer.fetch_users(call=call, users=users)
            current_ix += len(users)

        except Exception as exc:
            logger.error(exc)
            logger.error(util.full_stack()) #don't care, if Ctrl+c is hit, does not handle it.  When you restart, it restarts from the last chunk (too much trouble to handle Ctrl + c).
            # you will get duplicate tweets, so what...
            pass

        users_config['current_ix'] = current_ix
        
        flash_cmd_config(users_config, users_config_filepath, output_folder)

        logger.info('COMPLETED -> (current_ix: [%d/%d])'%(current_ix, total))
        logger.info('PAUSE %ds to CONTINUE...'%WAIT_TIME)
        time.sleep(WAIT_TIME)
    else:
        logger.info('[collect_users] ALL COMPLETED')

def collect_tweets_by_user_ids(users_config_filepath, output_folder, config):

    apikeys = list(config['apikeys'].values()).pop()

    users_config = {}
    with open(os.path.abspath(users_config_filepath), 'r') as users_config_rf:
        users_config = json.load(users_config_rf)    

    for user_config_id in itertools.cycle(users_config):

        user_config = users_config[user_config_id]
        if ('remove' in user_config and user_config['remove']):
            continue

        user_id = user_config['user_id']
        since_id = user_config['since_id'] if 'since_id' in user_config else 1

        logger.info('REQUEST -> (user_id: [%d]; since_id: [%d])'%(user_id, since_id))

        remove = False

        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder = output_folder)
            since_id, remove = twitterCralwer.fetch_user_timeline(user_id, since_id=since_id)
        except Exception as exc:
            logger.error(exc)
            logger.error(util.full_stack())
            pass

        user_config['since_id'] = since_id
        user_config['remove'] = remove

        users_config[user_config_id] = user_config

        flash_cmd_config(users_config, users_config_filepath, output_folder)

        logger.info('COMPLETED -> (user_id: [%d]; since_id: [%d]; remove: [%s])'%(user_id, since_id, remove))
        logger.info('PAUSE %ds to CONTINUE...'%WAIT_TIME)
        time.sleep(WAIT_TIME)

def collect_user_relatinoships_by_user_ids(call, user_ids_config_filepath, output_folder, config):
    '''
        user_ids_config = {"current_ix": 0, "users": ["2969995619"]}
    '''
    apikeys = list(config['apikeys'].values()).pop()

    user_ids_config = {}
    with open(os.path.abspath(user_ids_config_filepath), 'r') as user_ids_config_rf:
        user_ids_config = json.load(user_ids_config_rf)

    current_ix = user_ids_config['current_ix'] if ('current_ix' in user_ids_config) else 0
    user_ids = user_ids_config['users'][current_ix:]

    total = len(user_ids)

    for user_id in user_ids:
        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder = output_folder)
            twitterCralwer.fetch_user_relationships(call=call, user_id=user_id)
            current_ix += 1 # one at a time... no choice
        except Exception as exc:
            logger.error(exc)
            logger.error(util.full_stack())
            pass    

        user_ids_config['current_ix'] = current_ix
        
        flash_cmd_config(user_ids_config, user_ids_config_filepath, output_folder)

        logger.info('COMPLETED -> (current_ix: [%d/%d])'%(current_ix, total))
        logger.info('PAUSE %ds to CONTINUE...'%WAIT_TIME)
        time.sleep(WAIT_TIME)
    else:
        logger.info('[%s] ALL COMPLETED'%(call))

def collect_places(call, places_config_filepath, output_folder, config):
    '''
        query: places_config_filepath = {"current_ix": 0, "places": ["Gainesville, FL", "Shanghai, China"]}
        ip: places_config_filepath = {"current_ix": 0, "places": ["74.125.19.104"]}
    '''

    apikeys = list(config['apikeys'].values()).pop()

    places_config = {}
    with open(os.path.abspath(places_config_filepath), 'r') as places_config_rf:
        places_config = json.load(places_config_rf)

    current_ix = places_config['current_ix'] if ('current_ix' in places_config) else 0

    places = places_config['places'][current_ix:]
    total = len(places)

    for place in places:
        try:
            twitterCralwer = TwitterCrawler(apikeys=apikeys, oauth2=False, client_args=CLIENT_ARGS, output_folder = output_folder)
            twitterCralwer.geo_search(call=call, query=place)
            current_ix += 1 # one at a time... no choice
        except Exception as exc:
            logger.error(exc)
            logger.error(util.full_stack())
            pass    

        places_config['current_ix'] = current_ix
        
        flash_cmd_config(places_config, places_config_filepath, output_folder)

        logger.info('COMPLETED -> (current_ix: [%d/%d])'%(current_ix, total))
        logger.info('PAUSE %ds to CONTINUE...'%WAIT_TIME)
        time.sleep(WAIT_TIME)
    else:
        logger.info('collect_places_by_[%s] ALL COMPLETED'%(call))

if __name__=="__main__":

    if (not os.path.exists('logs')):
        os.makedirs('logs')

    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="config.json that contains twitter api keys;", default="./config.json")
    parser.add_argument('-o','--output', help="output folder data", default="./data/")
    parser.add_argument('-cmd','--command', help="commands: search, timeline, tweets_by_ids", default=None)
    parser.add_argument('-cc','--command_config', help="existing progress data", default="search.json")
    parser.add_argument('-wait','--wait_time', help="wait time to check available api keys", type=int, default=5)

    args = parser.parse_args()

    if not args.command:
        sys.exit('ERROR: COMMAND is required')

    formatter = logging.Formatter('(%(asctime)s) [%(process)d] %(levelname)s: %(message)s')
    handler = logging.handlers.RotatingFileHandler(
        'logs/twitter_tracker_%s.log'%(args.command), maxBytes=50 * 1024 * 1024, backupCount=10)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info(sys.version)

    WAIT_TIME = args.wait_time

    output_folder = os.path.abspath(args.output)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(os.path.abspath(args.config), 'r') as config_f:
        config = json.load(config_f)

        try:
            if (args.command == 'search'):
                collect_tweets_by_search_terms(args.command_config, output_folder, config)
            elif (args.command == 'user_timelines'):
                collect_tweets_by_user_ids(args.command_config, output_folder, config)
            elif (args.command == 'tweets_by_ids'):
                collect_tweets_by_ids(args.command_config, output_folder, config)
            elif (args.command == 'tweets_by_id_range'):
                collect_tweets_by_id_range(args.command_config, args.output, config)
            elif (args.command == 'users_by_ids'):
                collect_users('user_id', args.command_config, args.output, config)
            elif (args.command == 'users_by_screen_names'):
                collect_users('screen_name', args.command_config, args.output, config)
            elif (args.command in ['/friends/ids', '/friends/list', '/followers/ids', '/followers/list']):
                collect_user_relatinoships_by_user_ids(args.command, args.command_config, args.output, config)
            elif (args.command == 'places_by_queries'):
                collect_places('query', args.command_config, args.output, config)
            elif (args.command == 'places_by_ips'):
                collect_places('ip', args.command_config, args.output, config)
            else:
                raise Exception("command not found!")
        except KeyboardInterrupt:
            logger.error('You pressed Ctrl+C! SO I JUST Killed myself...')
            pass
        except Exception as exc:
            logger.error(exc)
            logger.error(util.full_stack())
        finally:
            pass