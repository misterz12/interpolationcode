'''
Created on Aug 9, 2016

@author: ionut
'''

import logging
from rtree import index

import database
import settings
import utils

logger = logging.getLogger('processor')
_counties = None
_stations = None


def load_all_counties():
    global _counties
    _counties = database.get_all_counties()
    
    
def load_station_data():
    global _stations
    _stations = utils.get_station_data()


def process_day(day, daily_data, max_neigh=8, pw=2):
    
    idxs = {}
    reading_by_id = {}
    i = 1
    for code, values in daily_data.items():
        reading_by_id[i] = (code, values)
        bbox = (_stations[code]['lng'], _stations[code]['lat'], _stations[code]['lng'], _stations[code]['lat'])
        for k, v in values.items():  # @UnusedVariable
            if k == 'day':
                continue
            if k not in idxs:
                idxs[k] = index.Index() 
            idxs[k].insert(i, bbox)
        i += 1
        '''station = _stations[k]
        if station['county'] is None:
            station['county'] = borders.get_county(station['lng'], station['lat'])
            if not station['county']:
                logger.warning('no county for ws: %s' % station)
        '''
    readings = []
    for county in _counties:
        reading_data = {}
        for signal in settings.SIGNALS:
            near_stations = idxs[signal].nearest((county[1], county[2]), max_neigh)
            sumd = 0
            iv = 0
            wsum = 0
            for near_station in near_stations:
                reading = reading_by_id[near_station]
                s = _stations[reading[0]]
                d = utils.distance(county[1], county[2], s['lng'],s['lat'])
                if d > 100: #too far > 100 km
                    continue
                sumd += d
                wsum += 1 / (d ** pw)
                iv += 1 / (d**pw) * reading[1][signal]
            
            if wsum != 0:
                iv = iv / wsum
                if signal in ['TMIN', 'TMAX']: #the values are in tenths of degrees C
                    iv = iv / 10
            else:
                iv = None
            
            reading_data[signal] = iv
            
        reading = [day, county[0], reading_data]
        readings.append(reading)
    
    result = database.add_county_readings(readings)
    logger.info('day: %s, result: %d inserted readings, %d updated readings' % (day, result[0], result[1]))

    