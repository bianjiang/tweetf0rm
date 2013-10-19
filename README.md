tweetf0rm
=========

A Twitter crawler that helps you collect data from Twitter for research. Most of the heavy works are already done by [Twython](https://github.com/ryanmcgrath/twython). ``tweetf0rmer`` is just a collection of python scripts help to deal with errors such as connection failures. In most use cases, it will auto-restart when an exception occurs. Moreover, when the crawler exceeds the Twitter API's [rate limit](https://dev.twitter.com/docs/rate-limiting/1.1/limits), the crawler will pause itself and auto-restart later.

Currently, it can run on multiple computers and collaboratively ``farm`` tweets or twitter networks. The main communication channel is built on top of [redis](http://redis.io/) a high performance in-memory key-value store. It has its own scheduler that can balance the load of each worker machine. Moreover, multiple processes can also be run concurrently on each node with different http proxies (to work-around the twitter's rate limit).

It's quite stable for the things that I want to do; but I has been running some of the scripts for 15 days without many hiccups.

One of the long term goal is to use [boto](http://boto.readthedocs.org/en/latest/) to integrate with the Amazon EC2 cluster so that you can run multiple crawlers to workaround Twitter's API rate limit. Helps are welcome!

Installation
------------

None... just clone this and start using it. It's not that complicated yet to have a setup.py..

    git clone git://github.com/bianjiang/tweetf0rm.git

Dependencies
------------
To run this, you will need:
- [Twython](https://github.com/ryanmcgrath/twython)
- [futures](https://pypi.python.org/pypi/futures) if you are on Python 2.7
- [redis server](http://redis.io/) and [redis python library](https://pypi.python.org/pypi/redis)
- [requests](http://www.python-requests.org/en/latest/)


Features
------------

- Support running multiple crawler processes (through python ``multiprocessing``) with different proxies on single node;
- Support a cluster of nodes to collaboratively ``f0rm`` tweets.

##### I haven't tested Python 3 yet... 


How to use
------------

First, you'll want to login the twitter dev site and create an applciation at https://dev.twitter.com/apps to have access to the Twitter API!

After you register, create an access token and grab your applications ``Consumer Key``, ``Consumer Secret``, ``Access token`` and ``Access token secret`` from the OAuth tool tab. Put these information into a ``config.json`` under ``apikeys`` (see an example below).

You have to have a redis server setup ([redis quick start](http://redis.io/topics/quickstart)). Note that if you want to run multiple nodes, you will only need to have one redis instance, and that instance has to be reachable from other nodes. The ``redis_config`` needs to be specified in the ``config.json`` as well.

Even you only wants to run on one node with multiple crawler processes, you will still need a local redis server for coordinating the tasks.

		{
			"apikeys": {
				"i0mf0rmer01" :{
					"app_key":"CONSUMER_KEY",
					"app_secret":"CONSUMER_SECRET",
					"oauth_token":"ACCESS_TOKEN",
					"oauth_token_secret":"ACCESS_TOKEN_SECRET"
				},
				"i0mf0rmer02" :{
					"app_key":"CONSUMER_KEY",
					"app_secret":"CONSUMER_SECRET",
					"oauth_token":"ACCESS_TOKEN",
					"oauth_token_secret":"ACCESS_TOKEN_SECRET"
				},
				"i0mf0rmer03" :{
					"app_key":"CONSUMER_KEY",
					"app_secret":"CONSUMER_SECRET",
					"oauth_token":"ACCESS_TOKEN",
					"oauth_token_secret":"ACCESS_TOKEN_SECRET"
				}
			},
			"redis_config": {
				"host": "localhost",
				"port": 6379,
				"db": 0,
				"password": "iloveusm"
			},
			"verbose": "True",
			"output": "./data"
		}

The proxies need to be listed in ``proxy.json`` file like:

		{
			"proxies":["58.20.127.100:3128", "58.20.223.230:3128", "210.22.63.90:8080"]
		}

The proxy will be verified upon bootstrap, and only the valid ones will be kept and used (currently it's not switching to a different proxy when a proxy server goes down, but will be added soon). There are a lot free proxy servers available.

Remember that Twitter's rate limit is per account as as well as per IP. So, you should have at least one twitter API account per proxy. Ideally, you should more proxies than twitter accounts, so that ``tweetf0rm`` can switch to a different proxy, if one failed (haven't implemented yet, but higher on the list).

To start the ``f0rm", you can simply run:

	
	python bootstrap.py -c config.json -p proxy.json


To issue a command to the ``f0rm``, you are basically pushing commands to redis. The client side hasn't finished yet, but you can take a look at ``client_test.py`` in the ``tests`` folder, and see how the commands should look like, e.g.,
	
	cmd = {
	 	"cmd": "CRAWL_FRIENDS",
	 	"user_id": 1948122342,
	 	"data_type": "ids",
	 	"depth": 2,
	 	"bucket":"friend_ids"
	}
	
	cmd = {
		"cmd": "CRAWL_FRIENDS",
		"user_id": 1948122342,
		"data_type": "users",
		"depth": 2,
		"bucket":"friends"
	}
	
	cmd = {
		"cmd": "CRAWL_USER_TIMELINE",
		"user_id": 1948122342#53039176,
		"bucket": "timelines"
	} 

bucket determine where the results will be saved in the ``output`` folder (specified in ``config.json``). All twitter data are json encoded strings, and output files are normally named with the twitter user id, e.g., if you are crawling a user's timeline, all his/her tweets will be organized in the "timelines" sub-folder with his/her twitter id (numerical and unique identifier for each twitter user).



### License
------------

The MIT License (MIT)
Copyright (c) 2013 Jiang Bian (ji0ng.bi0n@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
