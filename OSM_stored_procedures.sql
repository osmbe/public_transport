CREATE OR REPLACE FUNCTION osm_stops_offset() RETURNS void AS $BODY$
  DECLARE
    l record;
    geom geometry;

  BEGIN
    FOR l IN SELECT osm_stops.ref_de_lijn, lon, lat  FROM OSM_stops
      LOOP geom := st_setSRID(st_Point(l.lon, l.lat),4326);
      SELECT ST_Distance(geom, dls.geom) AS distance FROM DL_stops dls
       WHERE dls.stopidentifier == l."ref:De_Lijn";

      UPDATE OSM_stops AS st
        SET st.geom = geom,
            st.offsetinmeters = distance
        WHERE st.stopid=l.stopid;
          RAISE NOTICE  '% set to %',st.geom, st.offsetinmeters;
     END LOOP;
   END
$BODY$ LANGUAGE plpgsql VOLATILE COST 11;
GRANT EXECUTE ON FUNCTION DL_filloutlines() TO polyglot;
