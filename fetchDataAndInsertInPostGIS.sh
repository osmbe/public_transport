#!/bin/bash

mkdir -p data/DL

echo "Fetch De Lijndata"
python DL_fetchData.py

if [ $? -eq 0 ]
then
  echo " Downloaded fresh data"
else
  echo " No new data online, test if data is in database"
  psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -t -A -c "SELECT 1 FROM DL_segments LIMIT 1;"

  if [[ $? -ne 0 ]]; then
    echo Tables for De Lijndata don\'t seem to be present
  else
    exit
  fi
fi

echo "Drop tables and recreate them"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f DL_reinitialiseDB.sql

echo "Copy CSV data into tables"
for FN in calendar places routes trips segments stops
do
    tail -n +1 data/$FN.csv | psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -c "COPY DL_$FN FROM STDIN WITH HEADER CSV DELIMITER AS ';';"
    read -rsp $'Press any key or wait 5 seconds to continue...\n' -n 1 -t 5;
done

echo "Define stored procedures"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f DL_storedprocedures.sql

echo "ALTER TABLE STOPS"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f DL_alterTableStops.sql

echo "CREATE INDEXES"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f DL_createIndexes_1.sql

echo "Process Data in DB"
python DL_processDatainDB.py

echo "CREATE INDEXES"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f DL_createIndexes_2.sql
