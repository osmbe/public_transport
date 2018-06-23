#!/usr/bin/env bash

mkdir -p data/IB

token=`curl -k -d "grant_type=client_credentials" -H "Authorization: Basic cTF0eUJHdFV4bjNHOElqQlplM012QUVxQW8wYTpGNVV6a0tQWkl5MTA5SDZ6VUozemFPVGg3WThh" https://opendata-api.stib-mivb.be/token | grep -o -P '(?<="access_token":").*(?=","scope)'`

curl -k -X GET --header "Accept: application/zip" --header "Authorization: Bearer $token" -o ./data/IB/IB_gtfs.zip "https://opendata-api.stib-mivb.be/Files/1.0/Gtfs"

unzip data/IB/IB_gtfs.zip -d data/IB

#echo "Drop tables and recreate them"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f IB_reinitialiseDB.sql

echo "Copy CSV data into tables"
for fn in `ls data/IB/*.STP`
do
    echo "FILENAME: $fn"
    cat $fn | psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -c "COPY IB_STOPS FROM STDIN WITH CSV HEADER DELIMITER AS '|' ENCODING 'UTF-8';"
    read -t15 -n1 -r -p 'Press any key in the next fifteen seconds...' key
done

exit

echo "Define stored procedures"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f IB_storedprocedures.sql

echo "ALTER TABLE STOPS"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f IB_alterTableStops.sql

echo "CREATE INDEXES"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f IB_createIndexes.sql
