#!/bin/bash

kill -9 `ps e | grep tweetf0rm | grep -v grep | awk '{print $1}'`
