'''
Created on Aug 5, 2016

@author: ionut
'''

import fiona
import logging
from rtree import Rtree
from shapely.geometry import shape

logger = logging.getLogger('memory')

logger.info('loading shp data')
_countries = fiona.open('/media/ionut/Work/gis/gadm28_levels.shp/gadm28_adm0.shp')
_states = fiona.open('/media/ionut/Work/gis/gadm28_levels.shp/gadm28_adm1.shp')
_counties = fiona.open('/media/ionut/Work/gis/gadm28_levels.shp/gadm28_adm2.shp')

logger.info('building county index')
_counties_idx = Rtree()
for county in _counties:
    geom = shape(county['geometry'])
    gid = int(county['id'])
    _counties_idx.insert(gid, geom.bounds)

logger.info('done')