tweetf0rmer
=========

A Twitter crawler that helps you collect data from Twitter for research. Most of the heavy works are already done by [Twython](https://github.com/ryanmcgrath/twython). ``tweetf0rmer`` is just a collection of python scripts help to deal with errors such as connection failures. In most use cases, it will auto-restart when an exception occurs. Moreover, when the crawler exceeds the Twitter API's [rate limit](https://dev.twitter.com/docs/rate-limiting/1.1/limits), the crawler will pause itself and auto-restart later.

It's quite stable for the things that I want to do; but I has been running some of the scripts for 15 days without many hiccups.

One of the long term goal is to use [boto](http://boto.readthedocs.org/en/latest/) to integrate with the Amazon EC2 cluster so that you can run multiple crawlers to workaround Twitter's API rate limit. Helps are welcome!

Installation
------------

None... just clone this and start using it. It's not that complicated yet to have a setup.py..

    git clone git://github.com/bianjiang/tweetf0rmer.git
    cd tweetf0rmer/scripts

Dependencies
------------
To run this, you will need:
- [Twython](https://github.com/ryanmcgrath/twython)
- [futures](https://pypi.python.org/pypi/futures) if you are on Python 2.7


Features
------------

##### I am developing this for my own research, but feature requests or contributions are welcome for sure... 
##### If you see a problem, put in a ticket... 

Currently, three different scripts are provided (to meet my own needs); and they are all under the ``scripts`` folder.

- Available scripts:
    - ``track_keywords.py``: Track a list of keywords (up to 4,000, as limited by Twitter API); and streaming all the Tweets that are related to these keywords; see Twitter API doc [status/filter](https://dev.twitter.com/docs/api/1.1/post/statuses/filter) 
    - ``crawl_user_networks.py``: Starting from a list of ``seed`` users, this script will go out and find all their ``friends`` (or ``follower`` based-on setting) and their friends' friends until it reaches certain ``depth``. This is often used to create a friendship network for network analysis.  
    - ``crawl_user_timelines.py``: This crawls a user's most recent tweets (up to 3,200, as limited by Twitter API).
    - ``twitter_crawler.py``: This basically combines ``crawl_user_networks.py`` and ``crawl_user_timelines.py``, so it will create the friendship network while crawling all the tweets from users in the network.

##### I haven't tested Python 3 yet... 


How to use
------------

First, you'll want to login the twitter dev site and create an applciation at https://dev.twitter.com/apps to have access to the Twitter API!

After you register, create an access token and grab your applications ``Consumer Key``, ``Consumer Secret``, ``Access token`` and ``Access token secret`` from the OAuth tool tab. Put these information into a ``apikeys.json`` in the following format.


		{
				"i0mf0rmer" :{
						"app_key":"CONSUMER_KEY",
						"app_secret":"CONSUMER_SECRET",
						"oauth_token":"ACCESS_TOKEN",
						"oauth_token_secret":"ACCESS_TOKEN_SECRET"
				}
		}

The rest are fairly straigtforward, you can try to run e.g., ``python crawl_user_timelines.py --help`` to get help information about the parameters of each script.

		
		$python crawl_user_timelines.py --help
		usage: crawl_user_timelines.py [-h] -a APIKEYS -c CRAWLER -s SEEDS -o OUTPUT

		optional arguments:
		  -h, --help            show this help message and exit
		  -a APIKEYS, --apikeys APIKEYS
		                        config file for twitter api key (json format)
		  -c CRAWLER, --crawler CRAWLER
		                        the crawler identifier; you can have multiple crawler
		                        accounts set in the apikeys.json; pick one
		  -s SEEDS, --seeds SEEDS
		                        the list of users you want to crawl their timelines;
		                        see crawl_user_timelines.json as an example
		  -o OUTPUT, --output OUTPUT
		                        define the location of the output (each user's
		                        timeline will be in its own file under this output
		                        folder identified by the user id


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
