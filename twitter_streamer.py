#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
twitter_streamer.py: 

KeywordsStreamer: straightforward class that tracks a list of keywords; most of the jobs are done by TwythonStreamer; the only thing this is just attach a WriteToHandler so results will be saved

'''

import logging
import logging.handlers

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

import sys
import os
import time
import datetime
import json

import twython
from util import full_stack, chunks, md5

class TwitterStreamer(twython.TwythonStreamer):

    def __init__(self, APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, output_folder='./data'):

        self.output_folder = os.path.abspath(output_folder)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        self.output_file = None
        self.error_file = None
        
        now = datetime.datetime.now()
        self._setup_output_filehandlers(now)
        self.counter = 0
        self.error = 0

        super(TwitterStreamer, self).__init__(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    def _setup_output_filehandlers(self, now):
        self.now = now

        month_folder = os.path.abspath('%s/%s'%(self.output_folder, now.strftime('%Y-%m')))

        if not os.path.exists(month_folder):
            os.makedirs(month_folder)

        if (self.output_file):
            self.output_file.close()

        if (self.error_file):
            self.error_file.close()

        self.output_file = open(os.path.abspath('%s/%s.json'%(month_folder, now.strftime("%Y%m%d"))), 'a+', newline='', encoding='utf-8')
        self.error_file = open(os.path.abspath('%s/%s.errors.json'%(month_folder, now.strftime("%Y%m%d"))), 'a+', newline='', encoding='utf-8')

    def on_success(self, tweet):

        self.counter += 1

        if ('text' in tweet and 'id' in tweet and 'created_at' in tweet and 'user' in tweet):
            self.output_file.write('%s\n'%json.dumps(tweet))
        else:
            self.error += 1
            self.error_file.write('%s\n'%json.dumps(tweet))

        if (self.counter % 10000 == 0):
            now = datetime.datetime.now()
            if (now.strftime("%Y%m%d") != self.now.strftime("%Y%m%d")):
                self._setup_output_filehandlers(now)

            logger.info("received: %d; errors: %d;"%(self.counter, self.error))
            
    def on_error(self, status_code, data):
         logger.warn('ERROR CODE: [%s]-[%s]'%(status_code, data))
        
    def close(self):
        self.disconnect()

def init_streamer(config, output_folder):
    
    apikeys = list(config['apikeys'].values()).pop()

    APP_KEY = apikeys['app_key']
    APP_SECRET = apikeys['app_secret']
    OAUTH_TOKEN = apikeys['oauth_token']
    OAUTH_TOKEN_SECRET = apikeys['oauth_token_secret']

    streamer = TwitterStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, output_folder=output_folder)

    return streamer


def collect_public_tweets(config, output_folder):

    streamer = init_streamer(config, output_folder)

    logger.info("start collecting.....")

    streamer.statuses.sample()

def filter_by_locations(config, output_folder, locations = None):

    with open(os.path.abspath(locations), 'r') as locations_f:

        geo_locations = json.load(locations_f)

        name = geo_locations['name']
        locations = geo_locations['locations']

        streamer = init_streamer(config, '%s/%s'%(output_folder,name))
    
        logger.info("start collecting for %s....."%(name))

        streamer.statuses.filter(locations=locations)


if __name__=="__main__":

    if (not os.path.exists('logs')):
        os.makedirs('logs')

    logger.info(sys.version)

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="config.json that contains twitter api keys;", default="./config.json")
    parser.add_argument('-o','--output', help="output folder data", default="./data/")
    parser.add_argument('-cmd','--command', help="command", default="sample")
    parser.add_argument('-cc','--command_data', help="command data", default=None)

    args = parser.parse_args()

    formatter = logging.Formatter('(%(asctime)s) [%(process)d] %(levelname)s: %(message)s')
    handler = logging.handlers.RotatingFileHandler(
        'logs/twitter_streamer_%s.log'%args.command, maxBytes=50 * 1024 * 1024, backupCount=10)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


    with open(os.path.abspath(args.config), 'r') as config_f:
        config = json.load(config_f)

        try:
            while(True):
                try:
                    if (args.command == 'locations'):
                        filter_by_locations(config, args.output, args.command_data)
                    else:
                        collect_public_tweets(config, args.output)
                except Exception as exc:        
                    logger.error(exc)
                    #logger.error(full_stack())
                
                time.sleep(10)
                logger.info("restarting...")
        except KeyboardInterrupt:
            logger.error('You pressed Ctrl+C!')
            pass
        finally:
            pass
