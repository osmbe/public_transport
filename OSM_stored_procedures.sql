CREATE OR REPLACE FUNCTION osm_stops_offset() RETURNS void AS $BODY$
  DECLARE
    l record;
    v_geom geometry;
    distance float;

  BEGIN
    FOR l IN SELECT ref_de_lijn, lon, lat  FROM OSM_stops
      LOOP v_geom := st_setSRID(st_Point(l.lon, l.lat),4326);
      SELECT ST_Distance(v_geom, geomdl) INTO distance FROM DL_stops
       WHERE stopidentifier = l."ref_de_lijn";
      RAISE NOTICE  '%  %',l.ref_de_lijn, distance;
      UPDATE OSM_stops
        SET geom = v_geom,
            offsetinmeters = distance
        WHERE ref_de_lijn = l.ref_de_lijn;
     END LOOP;
   END
$BODY$ LANGUAGE plpgsql VOLATILE COST 11;
GRANT EXECUTE ON FUNCTION DL_filloutlines() TO polyglot;
