ALTER TABLE TEC_stops
 ADD COLUMN description_normalised text,
 ADD COLUMN lat DOUBLE PRECISION, 
 ADD COLUMN lon DOUBLE PRECISION,
 ADD COLUMN osm_zone text,
 ADD COLUMN route_ref text,
 ADD COLUMN bustram text,
 ADD COLUMN zoneid integer;

SELECT AddGeometryColumn ('public','stops_tec','geomtec',4326,'POINT',2);
SELECT AddGeometryColumn ('public','stops_tec','geomosm',4326,'POINT',2);
