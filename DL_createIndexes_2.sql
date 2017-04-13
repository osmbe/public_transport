CREATE INDEX IF NOT EXISTS ix_dl_stopidentifier ON DL_stops (stopidentifier);
CREATE INDEX IF NOT EXISTS ix_dl_description ON DL_stops (description);
CREATE INDEX IF NOT EXISTS ix_dl_routepublicidentifier ON DL_routes (routepublicidentifier);
CREATE INDEX IF NOT EXISTS ix_dl_segmentstopid ON DL_segments (stopid);

--VACUUM ANALYZE --VERBOSE;

