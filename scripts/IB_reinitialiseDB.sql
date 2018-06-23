DROP TABLE IF EXISTS IB_stops CASCADE;

DROP TABLE IF EXISTS IB_routes;
CREATE TABLE TEC_routes
 ( routeid text NOT NULL PRIMARY KEY,
   routename text,
   routedescription1 text,
   routedescription2 text,
   routepublicidentifier text )
  WITH ( OIDS=FALSE );
ALTER TABLE TEC_routes OWNER TO polyglot;

DROP TABLE IF EXISTS IB_trips;
CREATE TABLE TEC_trips
 ( tripid text NOT NULL PRIMARY KEY,
   routeid text,
   direction integer,
   mode integer,
   type integer )
   WITH ( OIDS=FALSE );
ALTER TABLE TEC_trips OWNER TO polyglot;

DROP TABLE IF EXISTS IB_segments;
CREATE TABLE TEC_segments
 ( segmentid serial NOT NULL PRIMARY KEY,
   tripid text,
   stopid text,
   segmentsequence int,
   time text)
  WITH ( OIDS=FALSE );
ALTER TABLE TEC_segments OWNER TO polyglot;

CREATE TABLE IB_stops
 ( stop_id text NOT NULL PRIMARY KEY,
   stop_code text,
   stop_name text,
   stop_desc text,
   stop_lat float,
   stop_lon float,
   zone_id text,
   stop_url text,
   location_type text)
  WITH ( OIDS=FALSE );
ALTER TABLE TEC_stops OWNER TO polyglot;

