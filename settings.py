'''
Created on Aug 4, 2016

@author: ionut
'''

import logging
logging.basicConfig(level=logging.INFO, 
    format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

CONN_STRING = "dbname='weather' user='postgres' host='127.0.0.1' password='password'"

FTP_URL = 'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/%s'
SIGNALS = set(['PRCP', 'SNOW', 'SNWD', 'TMIN', 'TMAX'])
# PRCP = Precipitation (tenths of mm)
# SNOW = Snowfall (mm)
# SNWD = Snow depth (mm)
# TMAX = Maximum temperature (tenths of degrees C)
# TMIN = Minimum temperature (tenths of degrees C)

STATIONS_FILE = 'data/ghcnd-stations.txt'
#see ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
