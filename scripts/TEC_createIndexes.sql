DROP INDEX IF EXISTS ix_tripsrouteidtec;
DROP INDEX IF EXISTS ix_segmentstripidtec;
DROP INDEX IF EXISTS ix_segmentsstopidtec;
CREATE INDEX ix_tripsrouteidtec ON trips_tec(routeid);
CREATE INDEX ix_segmentstripidtec ON segments_tec (tripid);
CREATE INDEX ix_segmentsstopidtec ON segments_tec (stopid);
