ALTER TABLE table ADD COLUMN offsetinmeters integer;

SELECT AddGeometryColumn ('public','osm_stops','geomdl',4326,'POINT',2);
