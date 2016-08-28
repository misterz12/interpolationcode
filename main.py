'''
Created on Aug 4, 2016

@author: ionut
'''

import glob
import logging

import processor
import settings

logger = logging.getLogger('main')
logger.info('loading stations data file')
processor.load_station_data()

logger.info('loading all counties from database')
processor.load_all_counties()

readings_files = glob.glob(settings.READINGS_FOLDER)
for readings_file in readings_files:
    logger.info('loading readings data file: %s' % readings_file)
    weather_data = open(readings_file, 'r')
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
            logger.info('new day: %s -> %s, data: %d' % (previous_day, day, len(daily_data)))
            result = processor.process_day(previous_day, daily_data)
            daily_data = {}
        
        previous_day = day
        
    #process remaining data (last_day)
    result = processor.process_day(day, daily_data)
    