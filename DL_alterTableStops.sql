ALTER TABLE DL_stops
 ADD COLUMN lat DOUBLE PRECISION,
 ADD COLUMN lon DOUBLE PRECISION,
 ADD COLUMN route_ref text,
 ADD COLUMN zone integer;

SELECT AddGeometryColumn ('public','dl_stops','geomdl',4326,'POINT',2);

