CREATE INDEX IF NOT EXISTS ix_dl_routeidentifier ON DL_routes (routeidentifier);
CREATE INDEX IF NOT EXISTS ix_dl_routeversion ON DL_routes (routeversion);
CREATE INDEX IF NOT EXISTS ix_dl_tripsrouteid ON DL_trips(routeid);
CREATE INDEX IF NOT EXISTS ix_dl_segmentstripid ON DL_segments (tripid);

--VACUUM ANALYZE --VERBOSE;
