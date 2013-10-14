#!/bin/bash

#launchctl load ~/Library/LaunchAgents/homebrew.mxcl.redis.plist
#launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mongodb.plist

mongod
redis-server /usr/local/etc/redis.conf