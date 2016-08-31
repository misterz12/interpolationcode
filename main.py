'''
Created on Aug 4, 2016

@author: ionut
'''

import logging
import datetime

import processor
import settings
import utils


logger = logging.getLogger('main')
logger.info('loading stations data file')
processor.load_station_data()

logger.info('loading all counties from database')
processor.load_all_counties()

now = datetime.datetime.now()
filename = '%d.csv.gz' % now.year
utils.download_data(filename)
reading_file = 'sorted_%d.csv' % now.year
logger.info('loading readings data file: %s' % reading_file)
weather_data = open(reading_file, 'r')
previous_day = None
daily_data = {}
for line in weather_data:
    parts = line.strip().split(',')
    signal = parts[2]
    if signal not in settings.SIGNALS:
        continue

    code = parts[0]
    day = parts[1]
    value = float(parts[3])
    
    if code not in daily_data:
        daily_data[code] = {'day': day}
    
    daily_data[code][signal] = value
    
    if previous_day and previous_day != day:
        logger.info('processing day: %s, with %d entries' % (previous_day, len(daily_data)))
        try:
            result = processor.process_day(previous_day, daily_data)
        except Exception as e:
            logger.warning('cannot store data: %s' % e)
        daily_data = {}
    
    previous_day = day
    
#process remaining data (last_day)
logger.info('processing day: %s, with %d entries' % (previous_day, len(daily_data)))
result = processor.process_day(day, daily_data)