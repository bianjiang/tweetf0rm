#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.handlers
#import re

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='(%(asctime)s) [%(process)d] %(levelname)s: %(message)s')
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

import sys,json, argparse, os
import hashlib
def md5(data):
    return hashlib.md5(data).hexdigest()
# n is the number in one list element
def chunks(arr, n):
    return [arr[i:i+n] for i in range(0, len(arr), n)]

def generate_search_json(query_terms, geocodes, search_json_filename):

    with open(search_json_filename, 'w') as wf:
        results = {}

        if (not geocodes):
            geocodes = [None]

        for geocode in geocodes:
            #logger.info(geocode)
            current_query_terms = []
            querystring_length = 0

            for term in query_terms:
                querystring_length += (len(term) +  7)
                current_query_terms.append(term.lower())

                if (querystring_length > 200):

                    querystring = '%s'%(' OR '.join('("' + term.lower() + '")' for term in current_query_terms))

                    output_filename = md5(('%s_%s'%(geocode,querystring)).encode('utf-8'))

                    #logger.info(current_query_terms)
                    
                    results[output_filename] = {
                        "terms": current_query_terms,
                        "since_id": 0,
                        "geocode": geocode,
                        "querystring": querystring
                    }

                    current_query_terms = []
                    querystring_length = 0

            if (len(current_query_terms) > 0):
                querystring = '%s'%(' OR '.join('("' + term.lower() + '")' for term in current_query_terms))

                output_filename = md5(('%s_%s'%(geocode,querystring)).encode('utf-8'))

                #logger.info(current_query_terms)
                
                results[output_filename] = {
                    "terms": current_query_terms,
                    "since_id": 0,
                    "geocode": geocode,
                    "querystring": querystring
                }
                current_query_terms = []
                querystring_length = 0

        json.dump(results, wf)

def generate_search_json_with_search_terms_config(search_terms_config_file):

    search_terms_config = {}
    with open(os.path.abspath(search_terms_config_file), 'r') as search_terms_config_file_rf:
        search_terms_config = json.load(search_terms_config_file_rf)

    generate_search_json(search_terms_config['search_terms'], search_terms_config['geocodes'], search_terms_config['search_json_filename'])


if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help="search_terms_config.json;", default=None, required=True)
    args = parser.parse_args()

    generate_search_json_with_search_terms_config(args.config)