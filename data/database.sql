--Postgres database structure for interpolation code (ghcn)

--reading
CREATE TABLE readings(
    id bigserial PRIMARY KEY,
    day date NOT NULL,
    county_id integer REFERENCES adm2(gid),
    data jsonb,
    UNIQUE (day, county_id)
);

--CREATE INDEX ON readings(day); not needed due to the UNIQUE constraint
CREATE INDEX ON readings(county_id);