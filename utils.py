'''
Created on Aug 5, 2016

@author: ionut
'''

import logging
from math import radians, cos, sin, asin, sqrt

import settings

logger = logging.getLogger('utils')


def get_station_data():
    # AG000060590  30.5667    2.8667  397.0    EL-GOLEA                       GSN     60590
    station_file = open(settings.STATIONS_FILE, 'r')
    stations = {}
    for line in station_file:
        code = line[0:12].strip()
        station = {
            'lat': float(line[12:21]),
            'lng': float(line[21:31]),
            'alt': float(line[31:38]),
            'name': line[39:71].strip(),
            'county': None
        }
        stations[code] = station
    station_file.close()
    return stations



def distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


