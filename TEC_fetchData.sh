#!/bin/bash

function testPresence {
    filePresent=`ls -rt data/TEC*  | grep "[0-9]" | tail -n 1`
           }

#Let's assume we are going to have to process the data
needToProcessDownloadedData=1

#Was the file already downloaded previously? Keep track of the file name
testPresence
echo $filePresent
filePresentBefore=$filePresent

#Only download again if it's not present yet
wget -N -nd -r -l1 http://opendata.tec-wl.be/Current%20BLTAC/ -P data

#Again find the most recent file
testPresence
if [ $filePresentBefore==$filePresent ]; then
    echo TEC data online hasn\'t changed
    needToProcessDownloadedData=0
fi

#Now check the database for presence of TEC data
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -tAc "SELECT 1 FROM TEC_stops LIMIT 1;"

if [[ $? -ne 0 ]]; then
    echo Tables for TEC data don\'t seem to be present.
    needToProcessDownloadedData=1
fi

if ! [ $needToProcessDownloadedData ]; then
    echo "Latest version of TEC data already in database"
    exit 0
fi

# Now we are sure we have the latest version of TEC data and we can import it in the DB
cd data/
# Create data/TEC folder if not present yet
mkdir -p TEC
unzip `basename $filePresent` -d TEC

cd TEC/
rm -f {*.BLK,*.CAR,*.HRA,*.NTE,*.OPR,*.STP,*.VAL,*.VER}

for zipfile in `ls -rt TEC* | grep "TEC\w\w\.zip"`
do
    unzip -u $zipfile
    rm -f $zipfile
done

#echo "Drop tables and recreate them"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f ../../TEC_reinitialiseDB.sql
pwd
ls *.STP
echo "Copy CSV data into tables"
#find . -name "*.STP" | while read fn
for fn in `ls *.STP`
do
    echo "FILENAME: $fn"
    cat $fn | psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -c "COPY TEC_STOPS FROM STDIN WITH CSV HEADER DELIMITER AS '|' ENCODING 'LATIN1';"
    read -t15 -n1 -r -p 'Press any key in the next fifteen seconds...' key
done
cd ../..
echo "Define stored procedures"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f TEC_storedprocedures.sql

echo "ALTER TABLE STOPS"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f TEC_alterTableStops.sql

echo "CREATE INDEXES"
psql -h postgresql.ulyssis.org -p 5432 -U polyglot -d polyglot_PT_BEL -a -f TEC_createIndexes.sql

