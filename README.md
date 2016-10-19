# interpolationcode

##About
The purpose of this project is to process historic weather data from *GHCN* and integrate it with boundary data from *GADM*.

##Data Sources

 - GHCN weather data: ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/
 - GHCN station data: *ghcnd-stations.txt*
	 - download the data from ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt and make sure the path in `settings.py` (see below) is pointing to the correct location
 - GADM boundary data: http://www.gadm.org/ 

##Installation
###Postgres
Follow the installation [instructions](https://wiki.postgresql.org/wiki/Apt) and install Postgres and PostGiS:

 - add the repo to apt sources and import the repo key
 - install the packages: `sudo apt-get install postgresql-9.5 postgresql-9.5-postgis-2.2`
 - tweak Postgres performance settings in `/etc/postgresql/9.5/main/postgresql.conf`
 - create a password for the `postgres` database user by logging in as postgres and using `ALTER ROLE`
 - create a new database (`weather`) and install the postgis extension using `CREATE EXTENSION`
 - download the data from GADM, extract it and import the it using `shp2pgsql -s 4326 -I -g geom -c gadm28_adm0.shp public.adm0 | psql -q -h 127.0.0.1 -U postgres -d weather`; use the command for each level you want (*adm0*, *adm1*, *adm2* etc.)

###Python
The application has been tested using Python 3 which is already installed in Ubuntu.
Install the needed packages:

 -  `sudo apt-get install python3-pip postgresql-server-dev-9.5 libspatialindex-dev`
 - `sudo pip3 install psycopg2 rtree`
 - copy the source files or use git `git clone REPO_URL` and review the settings file

##Processing
There are two scripts that need to be used: `downloader.py` and `main.py`.

###Downloader
It is used to automatically retrieve and sort (see [Notes](#Notes) 1) data from the [FTP source](ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/by_year/). Before downloading files make sure you have enough disk space to hold the uncompressed data for the year span selected: `python downloader.py START_YEAR STOP_YEAR`.

###Main
Make sure the table structure is created by running the *CREATE* SQL commands in `data/database.sql`.
The main script has two operation modes (see [Notes](#Notes) 2,3,4):
 - process already downloaded data using `python main.py "DATA_FILES"`
 - process current year data: `python main.py`

##Querying
To retrieve information from the table use a query like:
`SELECT (readings.data->>'TMAX')::float
FROM readings INNER JOIN adm2 ON adm2.gid = readings.county_id
WHERE day = '2015-01-01' AND adm2.name_0='United States' AND name_1='Minnesota' AND name_2='Faribault'`

##Notes
1) The input data sorting is needed because I noticed there are a few entries that are not sorted (for example for 28th of February - 1st of March).

2)As the processing can take quite a long time it is recommended to run the download and processing scripts on multiple cores / machines by running multiple instances (for example one instance for each 50-100 years).

3) When running the main script make sure you use the double quotes if using shell expansion when specifying the input file path because otherwise the shell will expand it and it won't be correctly processed by the script; for example "data/sorted_19*.csv" include the double quotes.

4) Because for recent days data is being added after the day first becomes available in the file the main script will only process data older than at least 7 days to allow the data to be completed; this means the main script will have to be run after New Year using the previous year after the 8th of January so all data is imported.

5) The query uses  `->>` because the data is stored as JSON in Postgres; this allows us to process more or less signals in the future if needed.

6) The current version only processes stations in the United States; if other areas are needed one has to open the `database.py` file and edit `get_all_counties_query`.