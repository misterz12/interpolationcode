--Postgres database structure for interpolation code (ghcn)

--reading
CREATE TABLE readings(
    id bigserial PRIMARY KEY,
    day date NOT NULL,
    county_id integer REFERENCES adm2(gid),
    data jsonb,
    UNIQUE (day, county_id)
);

CREATE INDEX ON readings(day);
CREATE INDEX ON readings(county_id);