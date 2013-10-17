tweetf0rmer
=========

A Twitter crawler that helps you collect data from Twitter for research. Most of the heavy works are already done by [Twython](https://github.com/ryanmcgrath/twython). ``tweetf0rmer`` is just a collection of python scripts help to deal with errors such as connection failures. In most use cases, it will auto-restart when an exception occurs. Moreover, when the crawler exceeds the Twitter API's [rate limit](https://dev.twitter.com/docs/rate-limiting/1.1/limits), the crawler will pause itself and auto-restart later.

It's quite stable for the things that I want to do; but I has been running some of the scripts for 15 days without many hiccups.

One of the long term goal is to use [boto](http://boto.readthedocs.org/en/latest/) to integrate with the Amazon EC2 cluster so that you can run multiple crawlers to workaround Twitter's API rate limit. Helps are welcome!

Currently, it can run on multiple computers and collaboratively ``farm`` tweets or twitter networks. The main communication channel is built on top of [redis](http://redis.io/) a high performance in-memory key-value store. It has its own scheduler that can balance the load of each worker machine. Moreover, multiple processes can also be run concurrently provided with proxies (to work-around the twitter's rate limit).


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
- [redis server](http://redis.io/) and [redis python library](https://pypi.python.org/pypi/redis)
- [requests](http://www.python-requests.org/en/latest/)


Features
------------

TBD

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
