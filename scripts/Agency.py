import os
from typing import Dict, Any
from urllib.parse import urlencode

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

    def __init__(self, name, operator_specific_tags=None):
        if operator_specific_tags is None:
            self.operator_specific_tags = {'ref':       'ref',
                                           'route_ref': 'route_ref',
                                           'zone':      'zone'}
        else:
            self.operator_specific_tags = operator_specific_tags

        self.name = name
        # dictionaries indexed on identifiers used at the operator/agency
        self.lines = {}
        self.itineraries = {}  # {'3303': [PublicTransportRoute, PublicTransportRoute, PublicTransportRoute]}
        self.stops = {}

        self.map_layer = osm.MapLayer()

    def process_query_result(self, osm_data):
        self.map_layer.from_overpy(osm_data)
        self.populate_from_osm_data()

    def populate_from_osm_data(self):
        """After downloading data using overpy for a region, an operator or a line,
           this method inventorises all Stop, Line and Itinerary instances encountered in it.

           The identifiers used as keys in these dictionaries are the identifiers used
           by the agency."""
        for stop_id in osm.Stop.lookup:
            stop = osm.Stop.lookup[stop_id]  # type: Stop
            # A stop can consist of multiple OSM primitives
            for stop_object_member in stop.get_stop_primitives:  # type: RelationMember
                if isinstance(stop_object_member.primitive, osm.Primitive):
                    # in a Stop instance we can have a RelationMember with an actual
                    # OSM primitive
                    stop_primitive = stop_object_member.primitive
                else:
                    # Or we can simply have the OSM id
                    # TODO we should check primtype to distinguish nodes from ways
                    try:
                        stop_primitive = osm.MapLayer.primitives['nodes'][stop_object_member.id]
                    except KeyError:
                        try:
                            stop_primitive = osm.MapLayer.primitives['ways'][stop_object_member.id]
                        except KeyError:
                            # If the primitive wasn't downloaded, we won't be able to look
                            # at its tags
                            continue
                print(self.operator_specific_tags)
                if self.operator_specific_tags['ref'] in stop_primitive.tags:
                    self.stops[stop_primitive.tags[self.operator_specific_tags['ref']]] = stop
        for itinerary_id in osm.Itinerary.lookup:
            itinerary = osm.Itinerary.lookup[itinerary_id]
            if self.operator_specific_tags['ref'] in itinerary.route.tags:
                self.itineraries.setdefault(itinerary.route.tags[self.operator_specific_tags['ref']], []).append(itinerary)
        for line_id in osm.Line.lookup:
            line = osm.Line.lookup[line_id]
            if self.operator_specific_tags['ref'] in line.route_master.tags:
                self.lines[line.route_master.tags[self.operator_specific_tags['ref']]] = line

    def fetch_agency_data(self, sheet_url):
        """Downloads a Google Sheet and saves it locally"""
        try:
            # TODO check for internet connection before downloading
            with open(self.sheet_filename, 'wb') as out_file:
                shutil.copyfileobj(requests.get(sheet_url, stream=True).raw, out_file)
        except:
            return None

    def load_agency_data(self, timeout=90):
        lstat = os.lstat(self.sheet_filename)
        print(lstat)
        # TODO test if self.sheet_filename is present and older than an hour
        data = pd.read_excel(self.sheet_filename, sheet_name=None)
        #                                         sheet_name=None means to read all the sheets
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
        self.compare_stops()

        self.compare_lines()

        self.compare_itineraries()

    def compare_stops(self):
        for stop in self.stops:
            try:
                operator_stop = self.agency_data['stops'].loc[stop]
            except:
                for rm in self.stops[stop].get_stop_primitives:
                    rm.primitive.tags['created_by'] = "This stop doesn't seem to exist anymore"
                continue
            """
            # Compare name tag
            if self.stops[stop].tags['name'] != operator_stop.stopdescription:
                # print('stop name not equal')
                self.stops[stop].tags['name'] = operator_stop.stopdescription

            # Compare route_ref tag
            if self.stops[stop].tags[self.route_operator_specific_tags['ref']] != operator_stop.route_ref_calculated:
                # print('route_ref not equal')
                self.stops[stop].tags[self.route_operator_specific_tags['ref']] = operator_stop.route_ref_calculated
            """

    def compare_itineraries(self):
        for itinerary in self.itineraries:
            # find its counterpart in the operator data
            try:
                signatures = (self.agency_data['itineraries'].loc[int(itinerary)].values)  # type: str
            except:
                continue

            itineraries_signatures = (
                self.unmatched_stop_sequences(
                    itinerary,
                    self.discard_shorter_variants_of_telescopic_itineraries(signatures)
                )
            )

            for itsig in itineraries_signatures:
                # For all the remaining ones new route relations need to be created
                stop_members = []
                if itineraries_signatures[itsig]:
                    for stop_ref in itsig.split(','):
                        if stop_ref in self.stops:
                            stop = self.stops[stop_ref]
                            print(stop)
                            stop_members.extend(stop.get_stop_primitives)
                        else:
                            # TODO investigate how this can happen
                            print(stop_ref, 'stop not found in downloaded data', type(stop_ref))
                    new_itinerary = osm.Itinerary(map_layer=self.map_layer,
                                                  mode_of_transport='bus',
                                                  stops=stop_members,
                                                  extra_tags={'odbl': 'tttttt',
                                                              'operator': 'De Lijn',
                                                              }
                                                  )

    def unmatched_stop_sequences(self, itinerary, itineraries_signatures):
        route_signatures = {}
        for itin in self.itineraries[itinerary]:
            route_signatures[itin.route.id] = ",".join(self.create_stops_list(itin))

            if route_signatures[itin.route.id] in itineraries_signatures:
                # exact match, just remove this sequence from operator's signatures.
                # print (route_signatures[pt_route.id], 'matches exactly.')
                del itineraries_signatures[route_signatures[itin.route.id]]
            else:
                pass  # print ('no match yet for', route_signatures[pt_route.id])
            for rtsig in route_signatures:
                # The exact matches are already resolved, so now we need to try
                # and find which stops sequences from agency are closest.
                self.match_itineraries(itin, itineraries_signatures, route_signatures, rtsig)
        return itineraries_signatures

    def discard_shorter_variants_of_telescopic_itineraries(self, signatures):
        itineraries_signatures = {}
        for signature in signatures:
            # print(signature)
            for key in list(itineraries_signatures.keys()):
                # print(key)
                if signature[0] in key:
                    continue
                elif key in signature[0]:
                    del itineraries_signatures[key]
            itineraries_signatures[signature[0]] = True
        return itineraries_signatures

    def create_stops_list(self, itinerary):
        stopslist = []
        for stop in itinerary.stops:
            for stop_member in stop.get_stop_primitives:
                if stop_member.id in self.map_layer.primitives['nodes']:
                    nd = self.map_layer.primitives['nodes'][stop_member.id]
                else:
                    # not sure what to do if referred node is not in downloaded data
                    # The Overpass query should have downloaded all child objects
                    print(stop_member.id, ' was not found in downloaded data')
                    continue
                stopslist.append(nd.tags[self.operator_specific_tags['ref']])
        return stopslist

    def match_itineraries(self, itin, itineraries_signatures, route_signatures, rtsig):
        highest_score = 0.0
        best_match = ''
        for itsig in itineraries_signatures:
            if route_signatures[rtsig]:
                cur = SequenceMatcher(None, route_signatures[rtsig], itsig).ratio()
                if cur > highest_score:
                    best_match = itsig
                    highest_score = cur
                if highest_score > 0.6:
                    print('route signature with best match:', rtsig)

                    # need to find the itinerary with route relation id rtsig
                    stops_list = []
                    for stop in best_match.split(','):
                        if stop in self.stops:
                            stops_list.append(self.stops[stop])
                        else:
                            try:
                                stop_data = self.agency_data['stops'].loc[str(stop)]
                            except:
                                continue
                            stops_list.append(Stop(map_layer=self.map_layer,
                                                   primitive=osm.Node(map_layer=self.map_layer,
                                                                      tags={'name': stop_data.stopdescription,
                                                                            self.operator_specific_tags['ref']: stop_data.stopidentfier,
                                                                            'operator': 'De Lijn',
                                                                            'url': 'mijnlijn.be/' + stop_data.stopidentfier,
                                                                            }
                                                                      )
                                                   )
                                              )
                    itin.update_stops(stops_list)
                    route_signatures[rtsig] = None
                    itineraries_signatures[best_match] = None

    def compare_lines(self):
        for line in self.lines:
            for route_member in self.lines[line].route_master.members:
                if not (self.operator_specific_tags['ref'] in self.map_layer.primitives['relations'][route_member.id].tags):
                    self.map_layer.primitives['relations'][route_member.id].add_tag(self.operator_specific_tags['ref'], line)
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

    def write_xml_to_file(self, filename):
        self.map_layer.xml().write(filename)

    def send_to_josm(self, new_layer=True, layer_name='Data from operator'):
        remote_control_base_url = "http://127.0.0.1:8111/"
        filename = layer_name + '.osm'
        params = {'layer_name': layer_name}

        if new_layer:
            params['new_layer'] = 'true'

        self.write_xml_to_file(filename)

        if self.check_if_josm_is_running(remote_control_base_url):
            self.tell_josm_to_import_data_via_remote_control(filename, params, remote_control_base_url)
        else:
            print('JOSM is not running locally')
            # send our osm file to a remote location
            result = requests.post('https://file.io', files={'file': open(filename, 'rb')})
            remote_control_import_url = remote_control_base_url + "import?" + urlencode(params) + "&url=" + \
                                        result.json()['link']
            # and give the user a link to invoke JOSM through the browser
            # on their local machine
            print(remote_control_import_url)

    def check_if_josm_is_running(self, remote_control_base_url):
        """

        :type remote_control_base_url: str
        """
        try:
            response = requests.get("{0}version".format(remote_control_base_url))
        except:
            return False
        else:
            try:
                return response.json()
            except:
                return False

    def tell_josm_to_import_data_via_remote_control(self, filename, params, remote_control_base_url):
        response = None
        try:
            remote_control_import_url = remote_control_base_url + "import?" + urlencode(
                params) + "&url=" + "file://" + os.getcwd() + '/' + filename.replace(
                ' ', '%20')
            response = requests.get(remote_control_import_url)
            print(response)
        except:
            print('sending to', remote_control_import_url, 'failed')

        return response
