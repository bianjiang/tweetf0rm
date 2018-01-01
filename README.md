
#### The old version is in the `tweetf0rm_1_0` branch
* The old version hasn't been updated for several reasons. Primarily because (1) it's too tedious to setup `redis` for this; and (2) using proxies don't work well unless you have massive private premium proxy servers.  
* If you want to see the old version, you can go [old](https://github.com/bianjiang/tweetf0rm/tree/tweetf0rm_1_0).

## Note
* These are based on my use cases, which primarily for batch processing (e.g., continuously monitoring a set of public users and fetch their timelines).
* If there are missing functions, you are welcome to contribute and make pull requests.
* I do have a huge collection of tweets, see below **[Datasets](#datasets)** section, but **Twitter license (or at least the company's position on this) does not allow me redistribute the crawled data (e.g., someone asked the question a while back: https://dev.twitter.com/discussions/8232).**   If you want to get a hand on this dataset (e.g., through **collaboration**), contact me at <ji0ng.bi0n@gmail.com>.
* If you need `geocode` Twitter users (e.g., figure out where the user is from based on the `location` string in their profile), you can take a look at this [TwitterUserGeocoder](https://github.com/bianjiang/twitter-user-geocoder)
* **Post collect process** [tweeta](https://github.com/bianjiang/tweeta) is a set of convenience functions that might help you parse raw json tweets (and give you a `TweetaTweet` object so that you can access the tweet through functions (e.g., `tweet.tweet_id()` and `tweet.created_at()`)).
* Please cite any of these:
   * *Bian J, Zhao Y, Salloum RG, Guo Y, Wang M, Prosperi M, Zhang H, Du X, Ramirez-Diaz LJ, He Z, Sun Y. [Using Social Media Data to Understand the Impact of Promotional Information on Laypeople’s Discussions: A Case Study of Lynch Syndrome](https://www.jmir.org/2017/12/e414). J Med Internet Res 2017;19(12):e414. DOI: 10.2196/jmir.9266. PMID: 29237586*
   * *Bian J, Yoshigoe K, Hicks A, Yuan J, He Z, Xie M, Guo Y, Prosperi M, Salluom R, Modave F. [Mining Twitter to assess the public perception of the "Internet of things"](http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0158450). PLoS One. 2016 Jul 8;11(7):e0158450. doi: 10.1371/journal.pone.0158450. eCollection 2016. PMID: 27391760*
   * *Hicks A, Hogan WR, Rutherford M, Malin B, Xie M, Fellbaum C, Yin Z, Fabbri D, Hanna J, Bian J*. [Mining Twitter as a First Step toward Assessing the Adequacy of Gender Identification Terms on Intake Forms](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4765681/). AMIA Annu Symp Proc. 2015;2015:611-620. PMID: 26958196*

# Installation
None... just clone this and start using it.

    git clone git://github.com/bianjiang/tweetf0rm.git
    
## Dependencies
- [Twython](https://github.com/ryanmcgrath/twython)

Just do:

    pip install -r requirements.txt

# Usage

* First, you'll want to login the twitter dev site and create an applciation at https://dev.twitter.com/apps to have access to the Twitter API!
* After you register, create an access token and grab your applications ``Consumer Key``, ``Consumer Secret``, ``Access token`` and ``Access token secret`` from the OAuth tool tab. Put these information into a ``config.json`` under ``apikeys`` (see an example below).

```json
{
        "apikeys": {
                "i0mf0rmer01": {
                        "app_key": "APP_KEY",
                        "app_secret": "APP_SECRET",
                        "oauth_token": "OAUTH_TOKEN",
                        "oauth_token_secret": "OAUTH_TOKEN_SECRET"
                }
        }
}

```

## Command line options

In general,
* `-c`: the config file for Twitter API keys
* `-o`: the output folder (where you want to hold your data)
* `-cmd`: the command you want to run
* `-cc`: the config file for the command (each command often needs different config files, see examples below)
* `-wait`: wait `x` secs between calls (only in REST API access)

## Streaming API access

### Public sample 
- [statuses/sample](https://developer.twitter.com/en/docs/tweets/sample-realtime/overview/GET_statuse_sample)
- `-cmd`: `sample` (this is default)
```bash
# Get public tweets using streaming API
python twitter_streamer.py -c ../twittertracker-config/config_i0mf0rmer01.json -o /mnt/data2/twitter/sample/ -cmd sample
```
### Filter by `geo`
- [statuses/filter](https://developer.twitter.com/en/docs/tweets/filter-realtime/api-reference/post-statuses-filter)
- `-cmd`: `locations`
- `-cc`: e.g., `test_data/geo/US_BY_STATE_1.json` 
```bash
# Streaming API: get tweets within geo boundries defined in -cc test_data/geo/US_BY_STATE_1.json
python twitter_streamer.py -c ../twittertracker-config/config_i0mf0rmer02.json -o /mnt/data2/twitter/US_BY_STATE -cmd locations -cc test_data/geo/US_BY_STATE_1.json

```

## REST APIs


### Search and monitor a list of keywords
- [search/tweets](https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html)
- `-cmd`: `search`
- `-cc`: `test_data/search.json` 

```json
{  
   "keyword_list_0":{  
      "geocode":null,
      "terms":[  
         "\"cervarix\"",
         "\"cervical cancer\"",
         "\"cervical #cancer\"",
         "\"#cervical cancer\"",
         "\"cervicalcancer\"",
         "\"#cervicalcancer\""
      ],
      "since_id":1,
      "querystring":"(\"cervarix\") OR (\"cervical cancer\") OR (\"cervical #cancer\") OR (\"#cervical cancer\") OR (\"cervicalcancer\") OR (\"#cervicalcancer\")"
   }, 
   "keyword_list_1": {
      "geocode": [
      "dona_ana_nm",
      "32.41906196127472,-106.82334114385034,51.93959956432837mi"
      ],
      "querystring": "(\"cancer #cervical\") OR (\"cancercervical\") OR (\"#cancercervical\")",
      "since_id": 0,
       "terms": [
         "cancer #cervical",
         "cancercervical",
         "#cancercervical"
       ]
   }
}
```
```bash
# Search using a search config file
python twitter_tracker.py -c ../twittertracker-config/config_i0mf0rmer08.json -cmd search -o data/search_query -cc test_data/search.json -wait 5
```
* It will output the file into a folder with the current timestamp ('YYYYYMMDD') with a filename derived from md5(querystring).
* This one has no end, it will continuously query Twitter for any new tweets matching the query.
* The reason that I'm using `search/tweets` rather than the streaming API `statuses/filters` (with the `track` option) is that often time I want to get old tweets as well (even through it's just a few days old.  Twitter only provide roughly a week old tweets when you do your search; while `statues/filters` does not provide any `old` tweets at all).
* The other caveat is that you can only track a limited number of keywords with `statues/filter`.  So, if you have a lot to track, you will need to have a lot of separate instances, each tracking different part of the keywords.
* With `search/tweets`, you can just search a portion of the keyword list at a time (when this happens take a look at the `test_scripts/generate_search_json.py`, which break a long list of keywords down into small portions, and generate the necessary config file for this).
* Note that you can also set the `geocode` field to constrain the search within that areas. 

### Monitor and fetch users' timelines
* [statuses/user_timelines](https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline)
* `-cmd`: `user_timelines`
* `-cc`: `test_data/user_timelines.json`
```json
{  
   "2969995619":{  
      "remove":false,
      "user_id":2969995619,
      "since_id":1
   }
}
```
* `remove` is used to track users whose timelines cannot be pulled (e.g., private, etc.), and it will not crawl `removed` user ids.

```bash
# Monitor and fetch users' timelines
python twitter_tracker.py -c ../twittertracker-config/config_i0mf0rmer08.json -cmd user_timelines -o data/timelines -cc test_data/user_timelines.json -wait 5
```

### Get tweets by a list of ids
* [statues/lookup](https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-lookup)
* `-cmd`: `tweets_by_ids`
* `-cc`: see below

```json
{"current_ix": 0, "tweet_ids": ["911333326765441025", "890608763698200577"]}
```
* It grabs upto 100 (per Twitter API limit) number of tweets from the `tweet_ids` list.
* It assumes the `tweet_ids` is unique, and if it stops (e.g., 'CTRL+C', it will remember it `current_ix`, when you restart, it starts from there)
```bash
python twitter_tracker.py -c ../twittertracker-config/config_i0mf0rmer08.json -o data/tweets_by_ids -cmd tweets_by_ids -cc test_data/tweet_ids.json
```

### Get tweets by an id range
* [statues/lookup](https://developer.twitter.com/en/docs/tweets/post-and-engage/api-reference/get-statuses-lookup)
* `-cmd`: `tweets_by_id_range`
* `-cc`: see below

```json
{"end_id": 299, "current_id": 0}
```
* We can use this to fetch historical data, e.g,. `search_history.json` as shown above, which starts at tweet_id = 0, and fetch 100 tweets in each iteratation and move the current_id to += 100, until it reaches `end_id`.
Note, it does NOT fetch `tweet_id == end_id` (up to end_id - 1)
```bash
python twitter_tracker.py -c ../twittertracker-config/config_i0mf0rmer08.json -o data/tweets_id_range -cmd tweets_by_id_range -cc test_data/tweets_id_range.json
```

### Get user objects by user ids
* [users/lookup](https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup)
* `-cmd`: `users_by_ids`
* `-cc`: see blow
```json
{"current_ix": 0, "users": ["2969995619"]}
```
```bash
python twitter_tracker.py -c ../twittertracker-config/config_i0mf0rmer08.json -o data/users_by_ids -cmd users_by_ids -cc test_data/user_ids.json
```

### Get user objects by screen names
* [users/lookup](https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup)
* `-cmd`: `users_by_screen_names`
* `-cc`: see blow
```json
{"current_ix": 0, "users": ["meetpacific"]}
```
```bash
python twitter_tracker.py -c ../twittertracker-config/config_i0mf0rmer08.json -o data/users_by_screen_names -cmd users_by_screen_names -cc test_data/user_screen_names.json
```

### Collect ['/friends/ids', '/friends/list', '/followers/ids', '/followers/list']
```json
{"current_ix": 0, "users": ["2969995619"]}
```
```bash
# /friends/ids
python twitter_tracker.py -c ../twittertracker-config/config_i0mf0rmer08.json -o data/friends_ids -cmd '/friends/ids' -cc test_data/user_ids.json

# /followers/ids
python twitter_tracker.py -c ../twittertracker-config/config_i0mf0rmer08.json -o data/followers_ids -cmd '/followers/ids' -cc test_data/user_ids.json
```
* `*/ids` only fetches `ids` (5,000 at a time), while `*/list` fetches the actual `user` objects (100 at a time).
* Note the differences between this and fetching user timelines.
   * In `timeline`, we want to keep tracking the users and get their latest tweets; while in this case, we only care about a snapshot of their relations.  So, this will stop when it has looped through the entire list.

### Search for `place` by either a `query` or `ip`
* [geo/search](https://developer.twitter.com/en/docs/geo/places-near-location/api-reference/get-geo-search)
* `-cmd`: `collect_places_by_[query/ip]`
* `-cc`: see blow
```json
{"current_ix": 0, "places": ["Gainesville, FL", "Shanghai, China"]}
{"current_ix": 0, "places": ["74.125.19.104"]}
```
```bash
# Search for `place` objects based on place names (query)
python twitter_tracker.py -c ../twittertracker-config/config_i0mf0rmer08.json -o data/places_by_queries -cmd places_by_queries -cc test_data/place_names.json

# Search for `place` based on `ip` addresses
python twitter_tracker.py -c ../twittertracker-config/config_i0mf0rmer08.json -o data/places_by_ips -cmd places_by_ips -cc test_data/ips.json
```
* Note, you will need a user context for these API endpoints (which means you have to provide `OAUTH_TOKEN` and `OAUTH_TOKEN_SECRET` in your config).


## </a>Datasets

**Twitter license (or at least the company's position on this) does not allow me redistribute the crawled data (e.g., someone asked the question a while back: https://dev.twitter.com/discussions/8232).**   If you want to get a hand on this dataset (e.g., through collaboration), contact me at <ji0ng.bi0n@gmail.com>.  But, here is what I have:

* **Random sample since 2014 (update: since 2009)**: I have been crawling tweets using [GET statuses/sample](https://dev.twitter.com/streaming/reference/get/statuses/sample) since 2014, nonstop... except a few days the server went down...
* **Tweets within US by states**: Using [POST statuses/filter](https://dev.twitter.com/streaming/reference/post/statuses/filter) with a `locations` filter by US states, since 10/16/2016.
* **Tweets related to HPV**: HPV related tweets using keywords such as “Human Papillomavirus”, “HPV”, “Gardasil” and “Cervarix” with the Twitter [Search API](https://dev.twitter.com/rest/public/search), since 02/2016 (as of today, 2/18/2017, it is still running).  I do have a similar dataset from 11/2/2015 till 02/2016, but that's from a friend.
* **Tweets related to transgender**: Tweets collected using keywords related to transgender (e.g., trans*, transmale, etc.) between 01/17/2015 and 05/12/2015; and then user timelines of whom are self-identified as trans.  This is published here, *"Hicks A, Hogan WR, Rutherford M, Malin B, Xie M, Fellbaum C, Yin Z, Fabbri D, Hanna J, Bian J. Mining Twitter as a First Step toward Assessing the Adequacy of Gender Identification Terms on Intake Forms. AMIA Annu Symp Proc. 2015;2015:611-620. PMID: [26958196](https://www.ncbi.nlm.nih.gov/pubmed/26958196)."*
* **Tweets related to lynch syndrome**: *Bian J, Zhao Y, Salloum RG, Guo Y, Wang M, Prosperi M, Zhang H, Du X, Ramirez-Diaz LJ, He Z, Sun Y. Using Social Media Data to Understand the Impact of Promotional Information on Laypeople’s Discussions: A Case Study of Lynch Syndrome. J Med Internet Res 2017;19(12):e414"* 
* **A few other MISC data sets**


## License

The MIT License (MIT)
Copyright (c) 2018 Jiang Bian (ji0ng.bi0n@gmail.com)

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


