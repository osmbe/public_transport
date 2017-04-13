CREATE OR REPLACE FUNCTION DL_AllLinesPassingAtaStop(stopidentifierparameter int) RETURNS text AS $BODY$
  DECLARE outlines text :='';
    l record;
    line text;
  BEGIN
    FOR l IN SELECT distinct(lpad(rte.routepublicidentifier, 5, '0'))
                                FROM DL_trips    trp
                                JOIN DL_routes   rte      ON rte.routeid=trp.routeid AND
                                                             rte.routepublicidentifier NOT LIKE 'F%'
                                JOIN DL_segments seg      ON seg.tripid=trp.tripid
                                JOIN DL_stops    stp      ON seg.stopid=stp.stopid
                                WHERE
                                  stp.stopidentifier = stopidentifierparameter
                ORDER BY lpad(rte.routepublicidentifier, 5, '0')
    LOOP
      line := l;
      line := trim(leading '(' FROM line);
      IF line = '00000'
      THEN line:= '0';
      ELSE line := trim(leading '0' FROM line);
      END IF;
      line := trim(trailing ')' FROM line);
      outlines := outlines || ';' || line;
    END LOOP;

    RETURN trim(both ';' FROM outlines);
  END $BODY$
LANGUAGE plpgsql VOLATILE COST 11;
GRANT EXECUTE ON FUNCTION DL_AllLinesPassingAtaStop(int) TO polyglot;

CREATE OR REPLACE FUNCTION DL_filloutlines() RETURNS void AS $BODY$
  DECLARE
    l record;
    res text;
    b text;
    a int4;
    coords geometry;
    vlat double precision;
    vlon double precision;

  BEGIN
    DROP INDEX IF EXISTS ix_geomDL;
    FOR l IN SELECT stopid, stopidentifier, x, y FROM DL_stops
      LOOP res := AllLinesPassingAtaStop(l.stopidentifier);
        coords := st_transform(st_setSRID(st_Point(l.x, l.y), 31370),4326);
        vlat := st_y(coords);
        vlon := st_x(coords);

      UPDATE DL_stops AS st
        SET route_ref=res,
          geomDL = coords,
          lat = vlat,
          lon = vlon
        WHERE st.stopid=l.stopid;
	  RAISE NOTICE  '% set to %',l.stopidentifier, res;
     END LOOP;
   END 
$BODY$ LANGUAGE plpgsql VOLATILE COST 11;
GRANT EXECUTE ON FUNCTION DL_filloutlines() TO polyglot;

