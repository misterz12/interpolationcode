'''
Created on Oct 13, 2016

@author: ionut
'''

import sys
import utils


def print_help_exit():
    print('usage: python downloader.py START_YEAR STOP_YEAR')
    print('\texample: python downloader.py 1893 2015')
    sys.exit(1)
    

if len(sys.argv) < 2:
    print_help_exit()

start_year = 0
stop_year = 0
try:
    start_year = int(sys.argv[1])
    stop_year = int(sys.argv[2])
    if not 1763 <= start_year <= stop_year <= 2016:
        raise Exception('invalid year')
except:
    print_help_exit()
    

for i in range(start_year, stop_year):
    filename = '%d.csv.gz' % i
    utils.download_data(filename)
