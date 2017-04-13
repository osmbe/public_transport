#!/bin/python
# -*- coding: utf-8 -*-

from dblogin import db

routescount = db.prepare('SELECT COUNT(*) FROM DL_routes;')
segmentscount = db.prepare('SELECT COUNT(*) FROM DL_segments;')
tripscount = db.prepare('SELECT COUNT(*) FROM DL_trips;')

print(routescount(), tripscount(), segmentscount())
print("Remove older route versions")
createDB = db.execute("""

    WITH currentversions AS (SELECT rte1.routeid FROM DL_routes rte1
                             WHERE rte1.routeversion = (SELECT MAX(rte2.routeversion)
                                                        FROM DL_routes rte2
                                                        JOIN DL_trips tr ON tr.routeid=rte2.routeid -- we want the highest version in the routes table for which there are actual trips
                                                        WHERE rte1.routeidentifier=rte2.routeidentifier))
    DELETE FROM DL_routes rte
      WHERE rte.routeid NOT IN (SELECT routeid from currentversions);
 """)

print("Remove trips for older route versions")
createDB = db.execute("""
DELETE FROM DL_trips trp
 WHERE NOT EXISTS
   (SELECT trp2.routeid FROM DL_trips trp2
     JOIN DL_routes rte ON trp2.routeid=rte.routeid
      AND trp.routeid=rte.routeid);
""")

print("Remove segments for older route versions")
createDB = db.execute("""
DELETE FROM DL_segments sgt
 WHERE NOT EXISTS (SELECT sgt2.segmentid FROM DL_segments sgt2
                     JOIN DL_trips trp ON sgt2.tripid=trp.tripid
                      AND sgt2.segmentid=sgt.segmentid);
""")

print(routescount(), tripscount(), segmentscount())
print("Converting from Lambert72 and adding route_ref to stops table")

filloutlines = db.proc('FillOutLines()')
filloutlines()

print("Creating index on description and spatial column containing coordinates from De Lijn")
createDB = db.execute("""

CREATE INDEX ix_geomDL ON DL_stops USING gist(geomDL);

""")

createDB = db.execute("""

VACUUM ANALYZE --VERBOSE;

""")

import IntegrateStopsFromOSM
IntegrateStopsFromOSM.main('data/PT.osm')

import DeLijnData_in_Postgis_2_OSM
DeLijnData_in_Postgis_2_OSM.main()

import CreateWikiReport
CreateWikiReport.main()
