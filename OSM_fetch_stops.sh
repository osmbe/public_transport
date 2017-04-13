python OSM_fetch_stops.py

psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f OSM_reinitialiseDB.sql

cat data/OSM_stops.csv | sed 's.\\.\\\\.g' | psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -c "COPY OSM_stops FROM STDIN;"
