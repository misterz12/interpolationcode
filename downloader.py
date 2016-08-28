'''
Created on Aug 28, 2016

@author: ionut
'''

import logging
import os
import subprocess
import urllib.request

import settings
logger = logging.getLogger('downloader')


for i in range(1893, 1951, 2):
    filename = '%d.csv.gz' % i
    logger.info('downloading %s' % filename)
    urllib.request.urlretrieve(settings.FTP_URL % filename, filename)
    logger.info('extracting %s' % filename)
    subprocess.call(['gunzip', filename])
    filename = filename.replace('.gz', '')
    logger.info('sorting %s' % filename)
    subprocess.call(['sort', '-t,', '-k', '2', '-o', 'sorted_%s' % filename, filename])
    os.remove(filename)