CREATE OR REPLACE VIEW OSM_DL_stops AS
 SELECT dl_stops.description, dl_stops.municipality,dl_stops.stopidentifier,
  dl_stops.stopisaccessible, dl_stops.parentmunicipality,
  dl_stops.lat AS DL_lat, dl_stops.lon AS DL_lon,
  dl_stops.geomdl, dl_stops.stopid, dl_stops.street, dl_stops.route_ref AS DL_route_ref,
  osm_stops.ref_de_lijn, osm_stops.name_de_lijn, osm_stops.zone_de_lijn,
  osm_stops.route_ref_tecb, osm_stops.route_ref_tecc, osm_stops.route_ref_tech,
  osm_stops.route_ref_tecl, osm_stops.route_ref_tecn, osm_stops.route_ref_tecx,
  osm_stops.route_ref_de_lijn, osm_stops.id, osm_stops.lat AS OSM_lat, osm_stops.lon AS OSM_lon,
  osm_stops.ref, osm_stops.name, osm_stops.type, osm_stops.zone, osm_stops.source,
  osm_stops.name_de, osm_stops.name_en, osm_stops.name_fr, osm_stops.name_nl,
  osm_stops.version, osm_stops.name_tec, osm_stops.operator,
  osm_stops.ref_tecb, osm_stops.ref_tecc, osm_stops.ref_tech,
  osm_stops.ref_tecl, osm_stops.ref_tecn, osm_stops.ref_tecx,
  osm_stops.username, osm_stops.zone_tec, osm_stops.route_ref AS OSM_route_ref,
  osm_stops.timestamp FROM dl_stops
 FULL JOIN osm_stops ON (dl_stops.stopidentifier = osm_stops.ref_de_lijn)
 WHERE dl_stops.stopispublic IS TRUE;
