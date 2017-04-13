CREATE OR REPLACE FUNCTION TEC_AllLinesPassingAtaStop(stopidentifierparameter text) RETURNS text AS $BODY$
  DECLARE outlines text :='';
    l record;
    line text;
    bustram text:='';
  BEGIN
    FOR l IN SELECT distinct(lpad(rte.routepublicidentifier, 5, '0')) AS publicidentifier
				FROM TEC_trips    trp
				JOIN TEC_routes   rte      ON rte.routeid=trp.routeid
				JOIN TEC_segments seg      ON seg.tripid=trp.tripid
				JOIN TEC_stops    stp      ON seg.stopid=stp.stopidentifier
				WHERE
				  stp.stopidentifier = stopidentifierparameter
                ORDER BY lpad(rte.routepublicidentifier, 5, '0')
    LOOP
      line := l.publicidentifier;
      line := trim(leading '(' FROM line);
      IF line = '00000'
      THEN line:= '0';
      ELSE line := trim(leading '0' FROM line);
      END IF;
      line := trim(trailing ')' FROM line);
      outlines := outlines || ';' || line;
    END LOOP;
    RETURN trim(both ';' FROM outlines) || ',' || bustram;
  END $BODY$
LANGUAGE plpgsql VOLATILE COST 100;
GRANT EXECUTE ON FUNCTION TEC_AllLinesPassingAtaTECStop(text) TO polyglot;

CREATE OR REPLACE FUNCTION TEC_filloutlines() RETURNS void AS $BODY$
  DECLARE
    l record;
    res text;
    b text;
    a int4;
    coords geometry;
    vlat double precision;
    vlon double precision;
    cityallcaps text;
    normalisedname text;
    description text;
  BEGIN
    DROP INDEX IF EXISTS ix_geomTEC;
    FOR l IN SELECT stopidentifier, descriptionfr, x, y FROM TEC_stops
      LOOP res := AllLinesPassingAtaTECStop(l.stopidentifier);
        coords := st_transform(st_setSRID(st_Point(l.x, l.y), 31370),4326);
        vlat := st_y(coords);
        vlon := st_x(coords);
        description := replace(l.descriptionfr, 'LE ROEULX', 'LE_ROEULX');
        description := replace(description, 'LE MESNIL', 'LE_MESNIL');
        description := replace(description, 'LE BRULY', 'LE_BRULY');
        description := replace(description, 'LE ROUX', 'LE_ROUX');
        description := replace(description, 'LE ROEULX', 'LE_ROEULX');
        description := replace(description, 'LA BOUVERIE', 'LA_BOUVERIE');
        description := replace(description, 'LA CALAMINE', 'LA_CALAMINE');
        description := replace(description, 'LA LOUVIERE', 'LA_LOUVIERE');
        description := replace(description, 'LA HESTRE', 'LA_HESTRE');
        description := replace(description, 'LA ROCHE-EN-ARDENNE', 'LA_ROCHE-EN-ARDENNE');
        description := replace(description, 'LA GLANERIE', 'LA_GLANERIE');
        description := replace(description, 'LA GLEIZE', 'LA_GLEIZE');
        description := replace(description, 'PETIT RY', 'PETIT_RY');
        description := replace(description, 'Eglise', 'Église');
        description := replace(description, 'Ecole', 'École');
        description := replace(description, 'St-', 'Saint-');
        description := replace(description, 'Ste-', 'Sainte-');
        description := replace(description, 'Av.', 'Avenue');
        cityallcaps := split_part(description,' ',1);
        SELECT normalised INTO normalisedname FROM cities WHERE AllCaps = cityallcaps;
      UPDATE TEC_stops
        SET route_ref=split_part(res,',',1),
          bustram=split_part(res,',',2),
          geomTEC = coords,
          lat = vlat,
          lon = vlon,
          description_normalised = replace(description,cityallcaps,normalisedname)
        WHERE TEC_stops.stopidentifier=l.stopidentifier;
	  RAISE NOTICE  '% set to %',l.stopidentifier, res;
     END LOOP;
   END 
$BODY$ LANGUAGE plpgsql VOLATILE COST 11;
GRANT EXECUTE ON FUNCTION TEC_filloutlines() TO polyglot;

CREATE OR REPLACE FUNCTION TEC_filloutzones() RETURNS void AS $BODY$
  DECLARE
    l record;
    res text;
    vzone text;
  BEGIN
    FOR l IN SELECT description_normalised FROM TEC_stops WHERE osm_zone IS NULL
      LOOP 
        SELECT osm_zone INTO vzone FROM TEC_stops s WHERE s.description_normalised = l.description_normalised;
      UPDATE TEC_stops
        SET osm_zone=vzone
        WHERE TEC_stops.description_normalised=l.description_normalised;
	  -- RAISE NOTICE  '% set to %'l.zone,vzone;
     END LOOP;
   END 
$BODY$ LANGUAGE plpgsql VOLATILE COST 11;
GRANT EXECUTE ON FUNCTION TEC_filloutzones() TO polyglot;

