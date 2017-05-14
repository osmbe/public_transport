#!/usr/bin/env bash
mkdir -p data/osm

python OSM_fetch_stops.py

psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f OSM_reinitialiseDB.sql

cat data/osm/stops.csv | sed 's.\\.\\\\.g' | psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -c "COPY OSM_stops FROM STDIN;"

psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f OSM_add_columns_to_stops.sql

