DROP TABLE IF EXISTS DL_stops CASCADE;

DROP TABLE IF EXISTS DL_places;
CREATE TABLE DL_places (
 placeid int NOT NULL PRIMARY KEY,
 placeidentifier text,
 placedescription text )
 WITH ( OIDS=FALSE );
ALTER TABLE DL_places OWNER TO polyglot;

DROP TABLE IF EXISTS DL_calendar;
CREATE TABLE DL_calendar (
 vscid int NOT NULL PRIMARY KEY,
 vsid bigint,
 vscdate date,
 vscday text )
 WITH ( OIDS=FALSE );
ALTER TABLE DL_calendar OWNER TO polyglot;

DROP TABLE IF EXISTS DL_routes;
CREATE TABLE DL_routes (
 routeid int NOT NULL PRIMARY KEY,
 routeidentifier text,
 routedescription text,
 routepublicidentifier text,
 routeversion text,
 routeservicetype text,
 routeservicemode text )
 WITH ( OIDS=FALSE );
ALTER TABLE DL_routes OWNER TO polyglot;

DROP TABLE IF EXISTS DL_trips;
CREATE TABLE DL_trips (
 tripid bigint NOT NULL PRIMARY KEY,
 routeid int REFERENCES DL_routes ON DELETE CASCADE,
 vscid int, --REFERENCES DL_calendar,
 tripnoteidentifier text,
 tripnotetext text,
 tripstart text,
 tripend text,
 tripshiftstart integer,
 tripshiftend integer,
 tripnoteidentifier2 text,
 tripnotetext2 text,
 placeidstart bigint REFERENCES DL_places,
 placeidend bigint REFERENCES DL_places,
 naturalkey text )
 WITH ( OIDS=FALSE );
ALTER TABLE DL_trips OWNER TO polyglot;

DROP TABLE IF EXISTS DL_segments;
CREATE TABLE DL_segments (
 segmentid bigint NOT NULL PRIMARY KEY,
 tripid bigint REFERENCES DL_trips ON DELETE CASCADE,
 stopid integer,
 segmentsequence integer,
 segmentstart text,
 segmentend text,
 segmentshiftstart integer,
 segmentshiftend integer )
 WITH ( OIDS=FALSE );
ALTER TABLE DL_segments OWNER TO polyglot;

DROP TABLE IF EXISTS DL_stops;
CREATE TABLE DL_stops (
 stopid INT NOT NULL PRIMARY KEY,
 stopidentifier text,
 description text,
 street text,
 municipality text,
 parentmunicipality text,
 x INT,
 y INT,
 stopisaccessible BOOLEAN,
 stopispublic BOOLEAN )
 WITH ( OIDS=FALSE );
ALTER TABLE DL_stops OWNER TO polyglot;

-- ALTER TABLE DL_segments ADD CONSTRAINT DL_segmentstopsfk FOREIGN KEY (stopid) REFERENCES DL_stops (stopid) MATCH FULL;
