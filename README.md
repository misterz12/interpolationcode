# interpolationcode

## About
The purpose of this project is to process historic weather data from *GHCN* and integrate it with boundary data from *GADM*.

## Data Sources

 - GHCN weather data: ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/
 - GHCN station data: *ghcnd-stations.txt*
	 - download the data from ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt and make sure the path in `settings.py` (see below) is pointing to the correct location
 - GADM boundary data: http://www.gadm.org/

## Installation
These installation instructions have been tested on a Ubuntu *14.04 LTS* AWS EC2 *c4.large* instance.

### Postgres
Follow the installation [instructions](https://wiki.postgresql.org/wiki/Apt) and install Postgres and PostGiS:

 - add the repo to apt sources and import the repo key
 - install the packages: `sudo apt-get install postgresql-9.5 postgresql-9.5-postgis-2.2`
 - tweak Postgres performance settings in `/etc/postgresql/9.5/main/postgresql.conf`
 - create a password for the `postgres` database user by logging in as postgres and using `ALTER ROLE`
 - create a new database (`weather`) and install the postgis extension using `CREATE EXTENSION`
 - download the adm level data in shapefile format from GADM for the whole world; current version is 2.8 available [here](http://biogeo.ucdavis.edu/data/gadm2.8/gadm28_levels.shp.zip)
 - extract the shapefile data and import it (use the command for each level needed: *adm0*, *adm1*, *adm2* etc.):

`shp2pgsql -s 4326 -I -g geom -c gadm28_adm0.shp public.adm0 | psql -q -h 127.0.0.1 -U postgres -d weather`

### Python
The application has been tested using Python 3 which is already installed in Ubuntu.
Install the needed packages:

 - `sudo apt-get install python3-pip postgresql-server-dev-9.5 libspatialindex-dev`
 - `sudo pip3 install psycopg2 rtree`
 - copy the source files or use `git clone REPO_URL` and review the settings file (paths, database connection details etc.)

## Processing
There are two scripts that need to be used: `downloader.py` and `main.py`.

### Downloader
It is used to automatically retrieve and sort (see [Notes](#notes) 1) data from the [FTP source](ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/). Before downloading files make sure you have enough disk space to hold the uncompressed data for the year span selected: `python downloader.py START_YEAR STOP_YEAR`.

### Main
Make sure the table structure is created by running the *CREATE* SQL commands in `data/database.sql`.
The main script has two operation modes (see [Notes](#notes) 2,3,4):
 - process already downloaded data using `python main.py "DATA_FILES"`
 - process current year data: `python main.py`

The results are calculated using the [IDW method](https://en.wikipedia.org/wiki/Inverse_distance_weighting) (Inverse Distance Weighting). For each administrative level (US counties by default) all stations within a 100 km distance that have valid readings are used to calculate the interpolated value. The application uses by default the closest 8 readings (parameter `max_neigh=8`) and the IDW *power parameter* is by default 2 (`pw=2`).
If there are less than 3 near samples that can be used for the calculation a warning message is logged containing the number of samples used. If there is no near sample available the interpolated value is `None` (`NULL` in the database).
For the temperature signals (`TMIN`, `TMAX`) an additional transformation is applied because the source data is in tenths of degrees C.
 
### Crontab
In order to process current year data on a daily basis one needs to setup a cron entry for it. The `run.sh` file is intended to be run from cron. For example to run the script each day at 09 AM use:

`0 9 * * * /home/ubuntu/icode/run.sh`

## Querying
To retrieve information from the table use a query like:
`SELECT (readings.data->>'TMAX')::float
FROM readings INNER JOIN adm2 ON adm2.gid = readings.county_id
WHERE day = '2015-01-01' AND adm2.name_0='United States' AND name_1='Minnesota' AND name_2='Faribault'`

## Notes

1) The input data sorting is needed because I noticed there are a few entries that are not sorted (for example for 28th of February - 1st of March).

2) As the processing can take quite a long time it is recommended to run the download and processing scripts on multiple cores / machines by running multiple instances (for example one instance for each 50-100 years).

3) When running the main script make sure you use the double quotes if using shell expansion when specifying the input file path because otherwise the shell will expand it and it won't be correctly processed by the script; for example "data/sorted_19*.csv" include the double quotes.

4) Because for recent days/weks data is being added after the day first becomes available in the data file the application will check the existing data and update the data with the new values only if they are different; this is to avoid table bloat in the Postgres database caused by excessive updating.

5) The query uses  `->>` because the data is stored as JSON in Postgres; this allows us to process more or less signals in the future if needed.

6) The current version only processes stations in the United States; if other areas are needed one has to open the `database.py` file and edit `get_all_counties_query`.

7) If one needs smaller regions to be processed (*adm3* and above) tweak the queries in the `database.py` file.

8) As more stations become available in the `ghcnd-stations.txt` file the local copy (in the data folder) needs to be updated so that the analysis can run successfully.
