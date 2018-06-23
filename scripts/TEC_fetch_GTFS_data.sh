#!/bin/bash

function testPresence {
    filePresent=`ls -rt data/TEC-GTFS*  | grep "[0-9]" | tail -n 1`
           }

#Let's assume we are going to have to process the data
needToProcessDownloadedData=1
#Was the file already downloaded previously? Keep track of the file name
testPresence
echo $filePresent
filePresentBefore=$filePresent

#Only download again if it's not present yet
wget -N -nd -r -l1 http://opendata.tec-wl.be/Current%20GTFS/ -P data

#Again find the most reent file
testPresence
if [ $filePresentBefore==$filePresent ]; then
    echo TEC online GTFS data hasn\'t changed
    needToProcessDownloadedData=0

fi
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -tAc "SELECT 1 FROM stops_tec LIMIT 1;"

if [[ $? -ne 0 ]]; then
    echo Tables for TEC data don\'t seem to be present
    needToProcessDownloadedData=1
fi

if ! [ $needToProcessDownloadedData ]; then
    echo "Latest version of TEC GTFS data already in database"
    exit 0
fi

# Now we are sure we have the latest version of TEC data and we can import it in the DB
cd data/
echo $filePresent
mkdir TEC
cd TEC/
unzip -u ../TEC-GTFS.zip

exit 0

for zipfile in `ls -rt TEC* | grep "TEC\w\w\.zip"`
do
    unzip -u $zipfile
    rm -f $zipfile
done

echo "Drop tables and recreate them"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f dropAndCreateTablesTEC.sql

echo "Copy CSV data into tables"
for fn in `ls *.STP`
do
    cat data/$fn.txt | psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -c "COPY $FN FROM STDIN WITH CSV HEADER DELIMITER AS ';';"
done


echo "Define stored procedures"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f storedprocedures.sql

echo "ALTER TABLE STOPS"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f alterTableStopsTEC.sql

echo "CREATE INDEXES"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f createIndexesTEC.sql

