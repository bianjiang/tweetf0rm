#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s-[%(module)s][%(funcName)s]: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

import sys, time, argparse, random, copy, pprint
sys.path.append(".")
from tweetf0rm.redis_helper import NodeQueue, NodeCoordinator
from tweetf0rm.utils import node_id, public_ip, hash_cmd
from tweetf0rm.exceptions import NotImplemented

pp = pprint.PrettyPrinter(indent=4)

avaliable_cmds = {
	'CRAWL_FRIENDS': {
		'user_id' : {
			'value':0,
			'validation': lambda x: x > 0
		},
		'data_type' : {
		 	'value': 'ids',
		 	'validation': lambda x: x in ['ids', 'users']
		},
		'depth': {
			'value': 1,
		},
		'bucket': {
			'value': 'friend_ids'
		}
	},
	'BATCH_CRAWL_FRIENDS': {
		'user_id' : {
			'value':0,
			'validation': lambda x: x > 0
		},
		'data_type' : {
		 	'value': 'ids',
		 	'validation': lambda x: x in ['ids', 'users']
		},
		'depth': {
			'value': 1,
		},
		'bucket': {
			'value': 'friend_ids'
		}
	},
	'CRAWL_FOLLOWERS': {
		'user_id' : {
			'value':0,
			'validation': lambda x: x > 0
		},
		'data_type' : {
		 	'value': 'ids',
		 	'validation': lambda x: x in ['ids', 'users']
		},
		'depth': {
			'value': 1,
		},
		'bucket': {
			'value': 'follower_ids'
		}
	},
	'BATCH_CRAWL_FOLLOWERS': {
		'user_id' : {
			'value':0,
			'validation': lambda x: x > 0
		},
		'data_type' : {
		 	'value': 'ids',
		 	'validation': lambda x: x in ['ids', 'users']
		},
		'depth': {
			'value': 1,
		},
		'bucket': {
			'value': 'follower_ids'
		}
	}, 'CRAWL_USER_TIMELINE': {
		'user_id' : {
			'value':0,
			'validation': lambda x: x > 0
		},
		'bucket': {
			'value': 'timelines'
		}
	},'CRAWL_TWEET': {
		'tweet_id' : {
			'value':0
		},
		'bucket': {
			'value': 'tweets'
		}
	}, 'BATCH_CRAWL_TWEET': {
		'bucket': {
			'value': 'tweets'
		}
	}, 'BATCH_CRAWL_USER_TIMELINE': {
		'bucket': {
			'value': 'timelines'
		}
	}, 'GET_UIDS_FROM_SCREEN_NAMES': {

	}, 'GET_USERS_FROM_IDS': {

	}, 'LIST_NODES':{

	}, 'SHUTDOWN_NODE': {

	}, 'NODE_QSIZES': {

	}, 'CLEAR_NODE_QUEUES': {

	}, 'SEARCH': {
		'query' : {
			'value': None,
			'validation': lambda x: x != None
		},
		'bucket': {
			'value': 'tweets'
		}
	}
}

from tweetf0rm.twitterapi.twitter_api import TwitterAPI
import json, os

def new_cmd(command, args_dict):

	cmd_template = avaliable_cmds[command]
	cmd = {'cmd':command}
	for k in cmd_template:
		cmd[k] = args_dict[k] if k in args_dict else cmd_template[k]['value']
		if ('validation' in cmd_template[k] and cmd_template[k]['validation']):
			if (not cmd_template[k]['validation'](cmd[k])):
				raise Exception("%s: %s failed validation"%(k, cmd[k]))

	cmd['cmd_hash'] = hash_cmd(cmd)

	return cmd

def cmd(config, args):
	
	if (args.command not in avaliable_cmds):
		raise Exception("not a valid command...")

	nid = args.node_id
	
	logger.info("node_id: %s"%(nid))
	node_queue = NodeQueue(nid, redis_config=config['redis_config'])
	node_coordinator = NodeCoordinator(config['redis_config'])
	# this can be done locally without sending the command to the servers...
	if (args.command == 'GET_UIDS_FROM_SCREEN_NAMES'):
		apikeys = config["apikeys"].values()[0]
		if (not os.path.exists(args.json)):
			raise Exception("doesn't exist... ")
		with open(os.path.abspath(args.json), 'rb') as f, open(os.path.abspath(args.output), 'wb') as o_f:
			screen_names = json.load(f)
			twitter_api = TwitterAPI(apikeys=apikeys)
			user_ids = twitter_api.get_user_ids_by_screen_names(screen_names)
			json.dump(list(user_ids), o_f)
	elif (args.command == 'GET_USERS_FROM_IDS'):
		apikeys = config["apikeys"].values()[0]
		if (not os.path.exists(args.json)):
			raise Exception("doesn't exist... ")
		with open(os.path.abspath(args.json), 'rb') as f, open(os.path.abspath(args.output), 'wb') as o_f:
			user_ids = json.load(f)
			twitter_api = TwitterAPI(apikeys=apikeys)
			users = twitter_api.get_users(user_ids)
			json.dump(list(users), o_f)
	elif (args.command.startswith('BATCH_')):
		new_command = args.command.replace('BATCH_', '')
		args_dict = copy.copy(args.__dict__)
		if (not os.path.exists(args.json)):
			raise Exception("doesn't exist... ")
		with open(os.path.abspath(args.json), 'rb') as f:
			if ( args.command == 'BATCH_CRAWL_TWEET' ):
				tweet_ids = json.load(f)
				for tweet_id in tweet_ids:
					print "Loading Tweet ID: ", tweet_id
					args_dict['tweet_id'] = tweet_id
					cmd = new_cmd(new_command, args_dict)
					node_queue.put(cmd)
			else:
				user_ids = json.load(f)
				for user_id in user_ids:
					args_dict['user_id'] = user_id
					cmd = new_cmd(new_command, args_dict)
					node_queue.put(cmd)
	elif (args.command == 'LIST_NODES'):
		pp.pprint(node_coordinator.list_nodes())
	elif (args.command == 'NODE_QSIZES'):
		raise NotImplemented("NotImplemented yet...")
		#pp.pprint(node_coordinator.list_nodes())
	elif (args.command == 'SHUTDOWN_NODE'):
		#node_coordinator.remove_node(nid)
		#pp.pprint(node_coordinator.list_nodes())
		raise NotImplemented("NotImplemented yet...")
	elif (args.command == 'CLEAR_NODE_QUEUES'):
		node_queue.clear_all_queues()
	else:
		args_dict = copy.copy(args.__dict__)
		cmd = new_cmd(args.command, args_dict)
		node_queue.put(cmd)
		logger.info('sent [%s]'%(cmd))

	

def print_avaliable_cmd():
	dictionary = {
		'-uid/--user_id': 'the user id that you want to crawl his/her friends (who he/she is following) or followers',
		'-tid/--tweet_id': 'the tweet id that you want to fetch',
		#'-nt/--network_type': 'whether you want to crawl his/her friends or followers',
		'-dt/--data_type': '"ids" or "users" (default to ids) what the results are going to look like (either a list of twitter user ids or a list of user objects)',
		'-d/--depth': 'the depth of the network; e.g., if it is 2, it will give you his/her (indicated by the -uid) friends\' friends',
		'-j/--json': 'a json file that contains a list of screen_names or user_ids, depending on the command',
		'-o/--output': ' the output json file (for storing user_ids from screen_names)',
		'-nid/--node_id':'the node_id that you want to interact with; default to the current machine...',
		'-q/--query': 'the query to search'
	}
	cmds =  {'CRAWL_FRIENDS': {
		'-uid/--user_id': dictionary['-uid/--user_id'],
		#'-nt/--network_type': dictionary['-nt/--network_type'],
		'-dt/--data_type': dictionary['-dt/--data_type'],
		'-d/--depth': dictionary['-d/--depth']
	}, 'BATCH_CRAWL_FRIENDS':{
		'-j/--json': dictionary['-j/--json'],
		#'-nt/--network_type': dictionary['-nt/--network_type'],
		'-dt/--data_type': dictionary['-dt/--data_type'],
		'-d/--depth': dictionary['-d/--depth']
	}, 'CRAWL_FOLLOWERS':{
		'-uid/--user_id': dictionary['-uid/--user_id'],
		#'-nt/--network_type': dictionary['-nt/--network_type'],
		'-dt/--data_type': dictionary['-dt/--data_type'],
		'-d/--depth': dictionary['-d/--depth']
	}, 'BATCH_CRAWL_FOLLOWERS':{
		'-j/--json': dictionary['-j/--json'],
		#'-nt/--network_type': dictionary['-nt/--network_type'],
		'-dt/--data_type': dictionary['-dt/--data_type'],
		'-d/--depth': dictionary['-d/--depth']
	}, 'CRAWL_USER_TIMELINE': {
		'-uid/--user_id': dictionary['-uid/--user_id']
	}, 'CRAWL_TWEET': {
		'-tid/--tweet_id': dictionary['-tid/--tweet_id']
	}, 'BATCH_CRAWL_TWEET': {
		'-j/--json': dictionary['-j/--json']
	}, 'BATCH_CRAWL_USER_TIMELINE': {
		'-j/--json': dictionary['-j/--json']
	}, 'GET_UIDS_FROM_SCREEN_NAMES': {
		'-j/--json':  dictionary['-j/--json'],
		'-o/--output':  dictionary['-o/--output']
	}, 'GET_USERS_FROM_IDS': {
		'-j/--json':  dictionary['-j/--json'],
		'-o/--output':  dictionary['-o/--output']
	}, 'LIST_NODES': {
	}, 'SHUTDOWN_NODE': {
		'-nid/--node_id':  dictionary['-nid/--node_id']
	}, 'NODE_QSIZES':{
		'-nid/--node_id':  dictionary['-nid/--node_id']
	}, 'CLEAR_NODE_QUEUES':{
		'-nid/--node_id':  dictionary['-nid/--node_id']
	}, 'SEARCH':{
		'-q/--query': dictionary['-q/--query']
	}}
	

	for k, v in cmds.iteritems():
		print('')
		print('\t%s:'%k)
		for kk, vv in v.iteritems():
			print('\t\t%s: %s'%(kk, vv))

	print('')


if __name__=="__main__":
	nid = node_id()
	import json, os
	
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument('-c', '--config', help="config.json that contains a) twitter api keys; b) redis connection string;", required = True)
	parser.add_argument('-cmd', '--command', help="the cmd you want to run, e.g., \"CRAWL_FRIENDS\"", required=True)
	parser.add_argument('-uid', '--user_id', help="the user_id", default=0)
	parser.add_argument('-tid', '--tweet_id', help="the tweet_id", default=0)
	parser.add_argument('-dt', '--data_type', help="the data_type (e.g., 'ids' or 'users'", default='ids')
	parser.add_argument('-d', '--depth', help="the depth", default=1)
	parser.add_argument('-j', '--json', help="the location of the json file that has a list of user_ids or screen_names", required=False)
	parser.add_argument('-o', '--output', help="the location of the output json file for storing user_ids", default='user_ids.json')
	parser.add_argument('-nid', '--node_id', help="the node_id you want to interact with", default=nid)
	parser.add_argument('-q', '--query', help="the search query", default=None)
	
	try:
		args = parser.parse_args()

		if args.command == 'HELP':
			print_avaliable_cmd()
			quit()

		with open(os.path.abspath(args.config), 'rb') as config_f:
			config = json.load(config_f)

			cmd(config, args)
	except Exception as exc:
		logger.error(exc)
		print_avaliable_cmd()