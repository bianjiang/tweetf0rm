#!/bin/bash

ulimit -S n 4096
PYTHONPATH=$PYTHONPATH:./tweetf0rm python ./tweetf0rm/bootstrap.py "$@"
