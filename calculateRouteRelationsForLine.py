#!/bin/python
# -*- coding: utf-8 -*-
import postgresql, re, sys, OSM_lib 
import argparse
import urllib.parse
from dblogin import *
from OSM_data_model import *

DL_servicetypes = ['regular','express','school','special','special','belbus']
OSM_servicetypes= ['',       'express','school','',       '',       'on_demand']
firstgroupsRE = re.compile(r'^(\d+;){3,4}')
lastgroupsRE = re.compile(r'(;\d+){3,4}$')


removePerronRE=re.compile(r"""(?xiu)
                              (?P<name>[\s*\S]+?)
                              (?P<perron>\s*-?\s*perron\s*\d(\sen\s\d)*)?
                              $
					       """) # case insensitive search to help remove (- )Perron #

routeidentifiersQUERY = db.prepare("""  SELECT DISTINCT
                                          rte.routeidentifier, rte.routedescription, rte.routepublicidentifier, rte.routeversion, rte.routeid
                                        FROM DL_routes   rte
                                        WHERE
                                          rte.routepublicidentifier ILIKE $1
                                          AND rte.routedescription !~* 'Feestbus'
                                        ORDER BY
                                          rte.routeidentifier;""")

tripids = db.prepare("""                SELECT DISTINCT
                                          trp.tripid,
                                          rte.routeservicetype AS type,
                                          rte.routeservicemode AS bustram,
                                          rte.routepublicidentifier,
                                          rte.routedescription AS routedescription,
                                          (SELECT 
                                              st1.description
                                              FROM 
                                                DL_stops st1
                                              JOIN DL_segments seg1 ON seg1.stopid = st1.stopid AND seg1.tripid = trp.tripid
                                              WHERE 
                                                seg1.segmentsequence = (SELECT MIN(seg2.segmentsequence) FROM DL_segments seg2 WHERE seg2.tripid = trp.tripid)) AS fromstop,
                                          (SELECT 
                                              st2.description
                                              FROM 
                                                DL_stops st2
                                              JOIN DL_segments seg3 ON seg3.stopid = st2.stopid AND seg3.tripid = trp.tripid
                                              WHERE 
                                                seg3.segmentsequence = (SELECT MAX(seg4.segmentsequence) FROM DL_segments seg4 WHERE seg4.tripid = trp.tripid)) AS tostop
                                        FROM DL_trips    trp
                                        JOIN DL_routes   rte      ON rte.routeid=trp.routeid
                                        JOIN DL_segments seg      ON seg.tripid=trp.tripid
                                        JOIN DL_stops    stp      ON seg.stopid=stp.stopid
                                        WHERE
                                          rte.routeidentifier = $1
                                        ORDER BY fromstop, tostop;""")
nodeIDsofStops = db.prepare("""SELECT DISTINCT
                                  stposm.id,
                                  stpdl.description,
                                  stpdl.description,
                                  stpdl.stopidentifier,
                                  trp.tripstart,
                                  seg.segmentsequence,
                                  stpdl.route_ref
                                FROM DL_trips     trp
                                JOIN DL_routes    rte      ON rte.routeid=trp.routeid
                                JOIN DL_segments  seg      ON seg.tripid=trp.tripid
                                JOIN DL_stops     stpdl    ON seg.stopid=stpdl.stopid
                                                           AND stpdl.description !~* 'dummy|afgeschaft'
                                JOIN OSM_stops    stposm   ON stpdl.stopidentifier = COALESCE(stposm.ref_De_Lijn, stposm.ref)
                                WHERE
                                  trp.tripid = $1
                                ORDER BY
                                  trp.tripstart ASC,
                                  seg.segmentsequence ASC;""")

upsert2Lines = db.prepare("""
INSERT INTO lines_line ( name, ref, publicref, operator, network, colour, mode, xml )
                VALUES ( $1, $2, $3, $4, $5, $6, $7, $8::text)
    ON CONFLICT (ref) DO
        UPDATE SET name = $1,
                   xml = $8::text;
""")

def processPT_line(ml, operator = 'De Lijn', lineref=''):
    distinctroutes = {}
    stops = []

    dlnetworks = ['An', 'OV', 'VB', 'Li', 'WV']
    if operator == 'TEC':
        network = 'TEC' + lineref[0]
    else:
        network = 'DL' + dlnetworks[int(lineref[0])-1]

    '''fetch all possible trips for this line'''
    tripslist = tripids(lineref)
    if not(tripslist): return None
    stopnames = {}
    stoprefs = {}
    stoprouterefs = {}
    for row in tripslist:
        print(row)
        stops_as_string = ','
        stopslist = nodeIDsofStops(row['tripid'])
        for stop in stopslist:
            stopnames[stop[0]] = stop[1]
            stoprefs[stop[0]] = stop[3]
            stoprouterefs[stop[0]] = stop[6]

            if stop[0]:
                if stop[0] != stops_as_string.split(',')[-2]:
                    stops_as_string += str(stop[0]).strip() + ','
            else:
                stops_as_string += '"' + str(stop[3]) + ';' + stop[1] + '",'
        stops_as_string = stops_as_string[1:-1]
        '''Remove shorter parts of "telescopic" itineraries'''
        notfound=True
        for sequence in distinctroutes.keys():
            notfound=True
            if len(stops_as_string)<len(sequence) and stops_as_string in sequence: notfound=False; break
            if len(sequence)<len(stops_as_string) and sequence in stops_as_string:
                del distinctroutes[sequence]
                break
        if notfound: distinctroutes[stops_as_string] = [row['fromstop'],row['tostop'],row['type'],row['bustram'],row['routepublicidentifier']]

    routeMaster = PT_RouteMaster(ml, tags={'public_transport:version': '2', 'odbl': 'tttttt'})
    '''We're only interested in the unique ones'''
    for stopssequence in distinctroutes:
        try:
            print(distinctroutes[stopssequence])
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )
        fromstop,tostop,servicetype,bustram,publicid = distinctroutes[stopssequence]
        if not(fromstop):
            fromstop='Naamloos'
        else:
            fromstop = OSM_lib.xmlsafe(fromstop)

        if not(tostop):
            tostop='Naamloos'
        else:
            tostop = OSM_lib.xmlsafe(tostop)

        try:
            print('\n' + str(i) + "  " + osmid + " " + fromstop + " - " + tostop)
        except:
            e = sys.exc_info()[0]
            print( "Error: %s" % e )

        route = PT_Route(ml, tags={'public_transport:version': '2', 'odbl': 'tttttt'})
        route.addTag('from', fromstop) 
        route.addTag('to', tostop)

        if int(bustram)==1 and not(operator == 'TEC'):
            route.addTag('route', 'tram')
            routeMaster.addTag('route_master', 'tram')
        else:
            route.addTag('route', 'bus')
            routeMaster.addTag('route_master', 'bus')

        route.addTag('name', operator + ' ' + publicid + ' ' +
                     re.search(removePerronRE,fromstop).group('name') + ''' - ''' +
                     re.search(removePerronRE,tostop).group('name'))
        route.addTag('ref', publicid)
        routeMaster.addTag('ref', publicid)
        route.addTag('operator', operator)
        routeMaster.addTag('operator', operator)
        route.addTag('network', network)
        routeMaster.addTag('network', network)
        if (servicetype and
             int(servicetype) in DL_servicetypes
             and DL_servicetypes[int(servicetype)]
             and not(operator == 'TEC')):
            route.addTag('bus', OSM_servicetypes[int(servicetype)])
            routeMaster.addTag('bus', OSM_servicetypes[int(servicetype)])
        if operator == 'TEC':
            route.addTag('ref:TEC', lineref)
            routeMaster.addTag('ref:TEC',  lineref)
        else:
            route.addTag('ref:De_Lijn', lineref)
            routeMaster.addTag('ref:De_Lijn', lineref)
    
        routeMaster.addRoute(route)
        for osmstopID in stopssequence.split(','):
            if osmstopID and osmstopID[0] == '"':
                osmstopID = stopssequence.split(',')[0].replace('"', '').strip()
                role = osmstopID.replace('"', '').strip()
                print('                                 ' + osmstopID + ' MISSING!!!!!!!!!!!!!')
            member = RelationMember(role = 'platform', primtype='node', member = osmstopID)
            route.addMember(member)
        routeMaster.addTag('name', operator + ' ' + publicid + ' ' + OSM_lib.xmlsafe(row['routedescription']))
    xml = ml.asXML
    upsert2Lines(routeMaster.tags['name'], routeMaster.tags['ref:De_Lijn'], routeMaster.tags['ref'],
                 routeMaster.tags['operator'], routeMaster.tags['network'], '', routeMaster.tags['route_master'], xml)
    return xml

def JOSM_RC(operator = '', lineref = ''):
    ml = MapLayer()
    processPT_line(ml, operator = 'De Lijn', lineref=lineref)
    osmXML = ml.asXML()
    values = { 'data': osmXML.replace('\n','').replace('\r',''),
               'new_layer': 'true',
               'layer_name': lineref} 
    data = urllib.parse.urlencode(values)
    return 'http://localhost:8111/load_data?{}'.format(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create route relations for each variation of a line')
    parser.add_argument('--route', '-r',
                       help="add a De Lirn route ref directly")
    parser.add_argument('--filename', '-f',
                       help="filename to write result")

    args = parser.parse_args()
    if args.route:
        url = JOSM_RC(operator = 'De Lijn', lineref=args.route)
        if args.filename:
            with open(args.filename, 'w') as fh:
               fh.write('''<html><a href={}>Data for {}<a/></html>'''.format(url, args.route))
        else:
            print(url)
