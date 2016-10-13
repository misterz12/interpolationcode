'''
Created on Aug 4, 2016

@author: ionut
'''

import datetime
import glob
import logging
import sys

import processor
import settings
import utils


logger = logging.getLogger('main')
logger.info('loading stations data file')
processor.load_station_data()

logger.info('loading all counties from database')
processor.load_all_counties()


readings_files = []
if len(sys.argv) > 1:
    try:
        readings_files.extend(glob.glob(sys.argv[1]))
        if len(readings_files) == 0:
            raise Exception('no files found in param')
    except Exception as e:
        logger.error('cannot process specified folder')
else:
    now = datetime.datetime.now()
    filename = '%d.csv.gz' % now.year
    utils.download_data(filename)
    readings_file = 'sorted_%d.csv' % now.year
    readings_files.append(readings_file)

    
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