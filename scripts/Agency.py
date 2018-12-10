import os
from typing import Dict, Any
from urllib.parse import urlencode

import overpy
import scripts.OSM_data_model as osm
from difflib import SequenceMatcher
import xlrd
import pandas as pd
import shutil
import requests

from scripts.OSM_data_model import Stop, RelationMember, MapLayer


class Agency:
    map_layer = ...  # type: MapLayer
    agency_data = {}  # type: Dict[str, pd.DataFrame]
    sheet_filename = 'temp.xlsx'

    def __init__(self, name, ref_tag='ref', route_ref_tag='route_ref', zone_tag='zone'):
        self.name = name
        # dictionaries indexed on identifiers used at the operator/agency
        self.lines = {}
        self.itineraries = {}  # {'3303': [PublicTransportRoute, PublicTransportRoute, PublicTransportRoute]}
        self.stops = {}

        self.ref_tag = ref_tag
        self.route_ref_tag = route_ref_tag
        self.zone_tag = zone_tag

        self.map_layer = osm.MapLayer()

    def perform_overpass_query(self, overpass_query):
        api = overpy.Overpass()
        if overpass_query:
            self.map_layer.from_overpy(api.query(overpass_query))
            self.populate_from_osm_data()

    def populate_from_osm_data(self):
        '''After downloading data using overpy for a region, an operator or a line,
           this method inventorises stops, lines and itineraries

           The identifiers used as keys in these dictionaries are the identifiers used
           by the agency.'''
        for stop_id in osm.Stop.lookup:
            stop = osm.Stop.lookup[stop_id]  # type: Stop
            for stop_object_member in stop.get_stop_objects:  # type: RelationMember
                if isinstance(stop_object_member.member, osm.Primitive):
                    stop_object = stop_object_member.member
                else:
                    try:
                        stop_object = osm.MapLayer.primitives['nodes'][stop_object_member.id]
                    except KeyError:
                        try:
                            stop_object = osm.MapLayer.primitives['ways'][stop_object_member.id]
                        except KeyError:
                            continue
                print(stop_object.id)
                if self.ref_tag in stop_object.tags:
                    self.stops[stop_object.tags[self.ref_tag]] = stop
        for itinerary_id in osm.Itinerary.lookup:
            itinerary = osm.Itinerary.lookup[itinerary_id]
            print(itinerary)
            if self.ref_tag in itinerary.route.tags:
                self.itineraries.setdefault(itinerary.route.tags[self.ref_tag], []).append(itinerary)
        for line_id in osm.Line.lookup:
            line = osm.Line.lookup[line_id]
            print(line_id, line.route_master)
            tags = line.route_master.tags
            if self.ref_tag in tags:
                self.lines[tags[self.ref_tag]] = line

    def fetch_agency_data(self, sheet_url):
        with open(self.sheet_filename, 'wb') as out_file:
            shutil.copyfileobj(requests.get(sheet_url, stream=True).raw, out_file)

    def load_agency_data(self):
        # TODO test if self.sheet_filename is present
        # sheet_name means to read all the sheets
        data = pd.read_excel(self.sheet_filename, sheet_name=None)
        stops = data['Stops']
        stops.stopidentifier = stops.stopidentifier.astype(str)
        self.agency_data = {'stops': stops.set_index('stopidentifier'),
                            'itineraries': data['Itineraries'].set_index('routeidentifier'),
                            'lines': data['Lines'].set_index('routeidentifier')}

    def update_using_operator_data(self):
        '''This method looks up details for each stop, line and itinerary we know about
        in the operator's data and updates them where needed'''

        if not self.agency_data:
            self.load_agency_data()
        for stop in self.stops:
            try:
                operator_stop = self.agency_data['stops'].loc[stop]
            except:
                self.stops[stop].tags['created_by'] = "This stop doesn't seem to exist anymore"
                continue
            """
            # Compare name tag
            if self.stops[stop].tags['name'] != operator_stop.stopdescription:
                # print('stop name not equal')
                self.stops[stop].tags['name'] = operator_stop.stopdescription

            # Compare route_ref tag
            if self.stops[stop].tags[self.route_ref_tag] != operator_stop.route_ref_calculated:
                # print('route_ref not equal')
                self.stops[stop].tags[self.route_ref_tag] = operator_stop.route_ref_calculated
            """

        for line in self.lines:
            for route_member in self.lines[line].route_master.members:
                if not (self.ref_tag in self.map_layer.primitives['relations'][route_member.id].tags):
                    self.map_layer.primitives['relations'][route_member.id].add_tag(self.ref_tag, line)
            try:
                operator_line = self.agency_data['lines'].loc[line]
            except:
                continue

            # Compare name tag
            if self.lines[line].tags['name'] != operator_line.name:
                print('line name not equal')
                self.lines[line].tags['name'] = operator_line.name
            else:
                print('line name equal')

        for itinerary in self.itineraries:
            itineraries_signatures = {}
            try:
                signatures = self.agency_data['itineraries'].loc[int(itinerary)].values
            except:
                continue
            for signature in signatures:
                for key in list(itineraries_signatures.keys()):
                    if signature[0] in key:
                        continue
                    elif key in signature[0]:
                        del itineraries_signatures[key]
                itineraries_signatures[signature[0]] = True

            route_signatures = {}
            for itin in self.itineraries[itinerary]:
                print(itin)
                stopslist = []
                for stop in itin.stops:
                    print(stop.platform_node)
                    for stop_prim in stop.get_stop_objects:
                        print(stop_prim)
                        if stop_prim.id in self.map_layer.primitives['nodes']:
                            nd = self.map_layer.primitives['nodes'][member.memberid]
                        else:
                            # not sure what to do if referred node is not in downloaded data
                            # The Overpass query should have downloaded all child objects
                            print(member.memberid, ' was not found in downloaded data')
                            continue
                        stopslist.append(nd.tags[self.ref_tag])
                route_signatures[itin.route.id] = ",".join(stopslist)

                if route_signatures[itin.route.id] in itineraries_signatures:
                    # exact match, just remove this sequence from operator's signatures.
                    # print (route_signatures[pt_route.id], 'matches exactly.')
                    del itineraries_signatures[route_signatures[itin.route.id]]
                else:
                    pass  # print ('no match yet for', route_signatures[pt_route.id])
            for rtsig in route_signatures:
                # The exact matches are already resolved, so now we need to try
                # and find which stops sequences from agency are closest.
                print(route_signatures[rtsig], 'does not match exactly')
                highest_score = 0.0
                best_match = ''
                for itsig in itineraries_signatures:
                    cur = SequenceMatcher(None, route_signatures[rtsig], itsig).ratio()
                    if cur > highest_score:
                        best_match = itsig
                        highest_score = cur
                if highest_score > 0.0:
                    # the stop members of   pt_route[rtsig]   need to be updated
                    print(len(itineraries_signatures))
                    stops_sequence = []
                    for stop in best_match.split(','):
                        stops_sequence.append(self.stops[stop].id)
                    self.itineraries[itinerary][rtsig].update_stops(stops_sequence)
                    del itineraries_signatures[best_match]

            for itsig in itineraries_signatures:
                # For all the remaining ones new route relations need to be created
                print('todo:', itsig)

    def send_to_josm(self, new_layer=True, layer_name = 'Data from operator'):
        url = "http://127.0.0.1:8111/"
        filename = layer_name + '.osm'
        params = {'layer_name': layer_name}

        if new_layer:
            params['new_layer'] = 'true'

        send_directly = True
        self.map_layer.xml().write(filename)
        try:
            response = requests.get(url + "version")
        except:
            send_directly = False
        else:
            try:
                json_response = response.json()
            except:
                send_directly = False
        if send_directly:
            try:
                url = url + "import?" + urlencode(params) + "&url=" + "file://" + os.getcwd() + '/' + filename.replace(' ', '%20')
                response = requests.get(url)
                print(response)
                print(url)
            except:
                print(url)
        else:
            print('JOSM is not running locally')
            # send our osm file to a remote location
            result = requests.post('https://file.io', files={'file': open(filename, 'rb')})
            url = url + "import?" + urlencode(params) + "&url=" + result.json()['link']
            # and give the user a link to invoke JOSM through the browser
            # on their local machine
            print(url)