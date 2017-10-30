DROP TABLE IF EXISTS TEC_stops CASCADE;

DROP TABLE IF EXISTS TEC_zones;
CREATE TABLE TEC_zones
 ( stopidentifier text NOT NULL PRIMARY KEY,
   zone text)
  WITH ( OIDS=FALSE );

DROP TABLE IF EXISTS TEC_cities;
CREATE TABLE TEC_cities
 ( AllCaps text NOT NULL PRIMARY KEY,
   Normalised text)
  WITH ( OIDS=FALSE );
ALTER TABLE TEC_cities OWNER TO polyglot;

DROP TABLE IF EXISTS TEC_routes;
CREATE TABLE TEC_routes
 ( routeid text NOT NULL PRIMARY KEY,
   routename text,
   routedescription1 text,
   routedescription2 text,
   routepublicidentifier text )
  WITH ( OIDS=FALSE );
ALTER TABLE TEC_routes OWNER TO polyglot;

DROP TABLE IF EXISTS TEC_trips;
CREATE TABLE TEC_trips
 ( tripid text NOT NULL PRIMARY KEY,
   routeid text,
   direction integer,
   mode integer,
   type integer )
   WITH ( OIDS=FALSE );
ALTER TABLE TEC_trips OWNER TO polyglot;

DROP TABLE IF EXISTS TEC_segments;
CREATE TABLE TEC_segments
 ( segmentid serial NOT NULL PRIMARY KEY,
   tripid text,
   stopid text,
   segmentsequence int,
   time text)
  WITH ( OIDS=FALSE );
ALTER TABLE TEC_segments OWNER TO polyglot;

CREATE TABLE TEC_stops
 ( stopidentifier text NOT NULL PRIMARY KEY,
   descriptionNL text,
   descriptionFR text,
   municipalityNL text,
   municipalityFR text,
   country text,
   streetNL text,
   streetFR text,
   ARI text,
   stopisaccessible INT,
   x INT,
   y INT,
   stopispublic INT,
   UIC text)
  WITH ( OIDS=FALSE );
ALTER TABLE TEC_stops OWNER TO polyglot;

