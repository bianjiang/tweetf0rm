#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

import sys
import json
import math

def explode(coords):
    """Explode a GeoJSON geometry's coordinates object and yield coordinate tuples.
    As long as the input is conforming, the type of the geometry doesn't matter."""
    for e in coords:
        if isinstance(e, (float, int, int)):
            yield coords
            break
        else:
            for f in explode(e):
                yield f

def bbox(f):
    x, y = zip(*list(explode(f['geometry']['coordinates'])))
    return min(x), min(y), max(x), max(y)

def to_bbox_polygon(bounding_box):

    min_x, min_y, max_x, max_y = bounding_box

    polygon = {
        'type': 'Polygon',
        'coordinates': [[
            [min_x, min_y],
            [min_x, max_y],
            [max_x, max_y],
            [max_x, min_y],
            [min_x, min_y]
        ]]
    }

    return polygon

MAX = 18
def process_us_states(geoJSON_file):
    with open(geoJSON_file) as gf:

        us = json.load(gf)
        logger.info(len(us['features']))
        
        name = []
        locations = []
        cnt = 0
        for state in us['features']:
            #logger.info(state['properties'])
            #min_x, min_y, max_x, max_y = bbox(state)

            name.append(state['properties']['NAME'])
            locations.append(','.join(['%s'%(x) for x in list(bbox(state))]))
            cnt += 1

            if (cnt % MAX == 0):
                n = 'US_BY_STATE_%d.json'%(math.ceil(cnt/MAX))
                with open(n, 'w') as wf:
                    json.dump({'name': n, 'locations': ','.join(locations)}, wf)
                
                name = []
                locations = []
            #logger.info(locations)
            #logger.info(json.dumps(to_bbox_polygon(bbox(state))))
        else:
            if (len(name) > 0):
                n = 'US_BY_STATE_%d.json'%(math.ceil(cnt/MAX))
                with open(n, 'w') as wf:
                    json.dump({'name': n, 'locations': ','.join(locations)}, wf)


def process_us_counties(geoJSON_file):
    with open(geoJSON_file, 'rb') as gf:
        us = json.loads(gf.read().decode('utf-8','ignore'))
        logger.info(len(us['features']))
        
        name = []
        locations = []
        cnt = 0
        
        florida = []
        for county in us['features']:
            if (county['properties']['STATE'] == '12'):
                florida.append(county)

        logger.info(len(florida))

def center(geolocations):

    """
    Provide a relatively accurate center lat, lon returned as a list pair, given
    a list of list pairs.
    ex: in: geolocations = ((lat1,lon1), (lat2,lon2),)
        out: (center_lat, center_lon)
    """
    from math import cos, sin, atan2, sqrt, pi
    x = 0
    y = 0
    z = 0

    for lat, lon in geolocations:
        lat = float(lat) * pi / 180
        lon = float(lon) * pi / 180
        x += cos(lat) * cos(lon)
        y += cos(lat) * sin(lon)
        z += sin(lat)


    x = float(x / len(geolocations))
    y = float(y / len(geolocations))
    z = float(z / len(geolocations))

    return (atan2(z, sqrt(x * x + y * y))  * 180 / pi, atan2(y, x) * 180 / pi)

def radius(geolocations):
    from geopy.distance import vincenty

    point_1, point_2 = geolocations

    return vincenty(point_1, point_2).miles/float(2)

#x is lon, y is lat NOTE
def find_county_by_name(name, state, geoJSON_file):
    import pandas as pd

    with open(geoJSON_file, 'rb') as gf:
        us = json.loads(gf.read().decode('utf-8','ignore'))

        for county in us['features']:

            if (county['properties']['STATE'] == state and name.lower() in county['properties']['NAME'].strip().lower()):

                min_x, min_y, max_x, max_y = bbox(county)
                logger.info(bbox(county))
                #logger.info(county)
                center_y, center_x = center(((min_y, min_x), (max_y, max_x),))

                r = radius(((min_y, min_x), (max_y, max_x)))
                
                logger.info(county)
                logger.info('%s,%s,%sm'%(center_x, center_y, r))
                quit()
                

if __name__=="__main__":

    logger.info(sys.version)

    process_us_states('gz_2010_us_040_00_20m.json')
    #process_us_counties('gz_2010_us_050_00_20m.json')

    # California 06
    # Texas 48
    # New Mexico 35
    # Arizona 04
    #find_county_by_name('Cochise', '04', 'gz_2010_us_050_00_20m.json')

