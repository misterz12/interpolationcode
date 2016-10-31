'''
Created on Aug 5, 2016

@author: ionut
'''

import psycopg2
import settings
from psycopg2._json import Json

connection = psycopg2.connect(settings.CONN_STRING)
connection.autocommit = True
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
    
    if not readings:
        return [0, 0]
    
    cursor.execute('SELECT day, county_id, data FROM readings WHERE day=%s', (readings[0][0], ))
    rows = cursor.fetchall()
    reading_by_county = {}
    for row in rows:
        reading_by_county[row[1]] = row[2]
        
    insert_readings = []
    update_readings = []
    for reading in readings:
        current_reading = reading_by_county.get(reading[1], None)
        if not current_reading:
            reading[2] = Json(reading[2])
            insert_readings.append(reading)
        else:
            different = False
            for k, v in reading[2].items():
                if v is None:
                    continue
                if current_reading.get(k, None) is None:
                    different = True
                    break
                if abs(v-current_reading[k]) > 0.001:
                    different = True
                    break
            
            if different:
                reading[2] = Json(reading[2])
                update_readings.append(reading)
    
    if insert_readings:
        data = ','.join(cursor.mogrify('(%s,%s,%s)', reading).decode('utf-8') for reading in insert_readings)
        cursor.execute('INSERT INTO readings(day, county_id, data) values ' + data)
    
    for reading in update_readings:
        cursor.execute('UPDATE readings SET data=%s WHERE day=%s AND county_id=%s', (reading[2], reading[0], reading[1]))
    
    return len(insert_readings), len(update_readings)
    