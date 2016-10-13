'''
Created on Aug 5, 2016

@author: ionut
'''

import psycopg2
import settings
from psycopg2._json import Json

connection = psycopg2.connect(settings.CONN_STRING)
cursor = connection.cursor()

get_county_query = "SELECT gid, ST_X(ST_Centroid(geom)) as clng, ST_Y(ST_Centroid(geom)) as clat, name_0, name_1, name_2 FROM adm2 WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) LIMIT 1"
get_county_fallback_query = """WITH data as (SELECT ST_SetSRID(ST_MakePoint(%s, %s), 4326) as point)
SELECT gid, ST_X(ST_Centroid(geom)) as clng, ST_Y(ST_Centroid(geom)) as clat, name_0, name_1, name_2 FROM adm2
WHERE ST_DWithin(geom, (SELECT point FROM data), 100) 
ORDER BY geom <#> (SELECT point FROM data) ASC LIMIT 1"""

#For whole world remove WHERE condition
get_all_counties_query = "SELECT gid, ST_X(ST_Centroid(geom)) as clng, ST_Y(ST_Centroid(geom)) as clat, name_0, name_1, name_2 FROM adm2 WHERE name_0 = 'United States'"


def get_county(lng, lat):
    data = float(lng), float(lat)
    cursor.execute(get_county_query, data)
    row = cursor.fetchall()
    if not row:
        cursor.execute(get_county_fallback_query, data)
        row = cursor.fetchall()
    return row[0]


def get_all_counties():
    cursor.execute(get_all_counties_query)
    rows = cursor.fetchall()
    return rows


def add_county_readings(readings):
    for reading in readings:
        reading[2] = Json(reading[2])
    data = ','.join(cursor.mogrify('(%s,%s,%s)', reading).decode('utf-8') for reading in readings)
    cursor.execute('INSERT INTO readings(day, county_id, data) values ' + data)
    connection.commit()
    
    