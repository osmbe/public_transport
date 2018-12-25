import math
import os
import re
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

    def __init__(self, name, operator_specific_tags=None, shorten_stop_nameRE=None):
        if operator_specific_tags is None:
            self.operator_specific_tags = {'ref':       'ref',
                                           'route_ref': 'route_ref',
                                           'zone':      'zone'}
        else:
            self.operator_specific_tags = operator_specific_tags
        if shorten_stop_nameRE:
            self.shorten_stop_nameRE = shorten_stop_nameRE
        else:
            self.shorten_stop_nameRE = re.compile(r"""(?xiu)
                                                      (?P<name>[\s*\S]+?)
                                                      (?P<platform>\s*-?\s*platform\s*\d(\sand\s\d)*)?
                                                      $
					                     """)

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
        print("Create lookup dictionaries based on ref used by agency")
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
        print("Download agency data from Google sheet")
        try:
            # TODO check for internet connection before downloading
            with open(self.sheet_filename, 'wb') as out_file:
                shutil.copyfileobj(requests.get(sheet_url, stream=True).raw, out_file)
        except:
            return None

    def load_agency_data(self, timeout=90):
        print("Read agency data into Pandas dataframes")
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

        print("Compare OSM data with agency data")
        if not self.agency_data:
            self.load_agency_data()
        self.compare_stops()

        self.compare_lines()

        self.compare_itineraries()

    def compare_stops(self):
        print("Compare stops")
        for stop in self.stops:
            try:
                operator_stop = self.agency_data['stops'].loc[stop]
            except:
                for rm in self.stops[stop].get_stop_primitives:
                    if rm.primitive:
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
        print("Compare itineraries (route relations)")
        print("Itineraries to start with", self.itineraries)
        for itinerary in self.itineraries:
            # find its counterpart in the operator data
            try:
                signatures = self.agency_data['itineraries'].loc[int(itinerary)].values  # type: str
            except:
                continue
            print('starting with:', len(signatures))
            itineraries_signatures = (
                self.unmatched_stop_sequences(
                    itinerary,
                    self.discard_shorter_variants_of_telescopic_itineraries(signatures)
                )
            )
            self.create_new_itineraries_for_remaining_stop_signatures(itineraries_signatures, itinerary)

    def create_new_itineraries_for_remaining_stop_signatures(self, itineraries_signatures, itinerary):
        print('remaining:', len(itineraries_signatures))
        for itsig in itineraries_signatures:
            # For all the remaining ones new route relations need to be created
            print(itsig, itineraries_signatures[itsig])
            stop_members = []
            if itineraries_signatures[itsig]:
                for stop_ref in itsig.split(','):
                    if stop_ref in self.stops:
                        stop = self.stops[stop_ref]
                        stop_members.extend(stop.get_stop_primitives)
                    else:
                        # TODO investigate how this can happen
                        print(stop_ref, 'stop not found in downloaded data', type(stop_ref))

                line_data_from_operator = self.agency_data['lines'].loc[int(itinerary)]
                nodes = self.map_layer.primitives['nodes']
                tags = {'ref': line_data_from_operator['routepublicidentifier'],
                        'from': nodes[stop_members[0].id].tags['name'],
                        'to': nodes[stop_members[-1].id].tags['name'],
                        'odbl': 'tttttt',
                        }
                if itinerary in self.lines:
                    line = self.lines[itinerary] # type: osm.Line
                    for tag in ['operator', 'operator:wikidata',
                                'network', 'network:wikidata',
                                'colour', 'url', 'bus',
                                self.operator_specific_tags['ref']]:
                        if tag in line.route_master.tags:
                            tags[tag] = line.route_master.tags[tag]
                    tags['name'] = ''
                    if 'operator' in tags:
                        tags['name'] += tags['operator']
                    if 'ref' in tags:
                        tags['name'] += ' ' + str(tags['ref'])
                    if 'from' in tags:
                        tags['name'] += ' ' + re.search(self.shorten_stop_nameRE,tags['from']).group('name')
                    if 'via' in tags:
                        tags['name'] += ' - ' + re.search(self.shorten_stop_nameRE,tags['via']).group('name')
                    if 'to' in tags:
                        tags['name'] += ' - ' + re.search(self.shorten_stop_nameRE, tags['to']).group('name')
                else:
                    # TODO If there is no route_master relation yet,
                    # it probably would need to be created (first)
                    print('no route master for:', itinerary)
                if str(line_data_from_operator['mode']):
                    tags['route'] = str(line_data_from_operator['mode'])

                if not math.isnan(line_data_from_operator['type']):
                    tags['bus'] = str(line_data_from_operator['type'])
                line.add_route(osm.Itinerary(map_layer=self.map_layer,
                                             mode_of_transport=line_data_from_operator['routeservicemode'],
                                             stops=stop_members,
                                             extra_tags=tags
                                             )
                               )

    def unmatched_stop_sequences(self, itinerary, itineraries_signatures):
        route_signatures = {}
        for itin in self.itineraries[itinerary]:
            print('itinerary',itin)
            route_signatures[itin.route.id] = ",".join(self.create_stops_list(itin))

            if route_signatures[itin.route.id] in itineraries_signatures:
                # exact match, just remove this sequence from operator's signatures.
                del itineraries_signatures[route_signatures[itin.route.id]]

            for rtsig in route_signatures:
                print('route signature',rtsig)
                # The exact matches are already resolved, so now we need to try
                # and find which stops sequences from agency are closest.
                self.match_itineraries(itin, itineraries_signatures, route_signatures, rtsig)
        return itineraries_signatures

    def discard_shorter_variants_of_telescopic_itineraries(self, signatures):
        itineraries_signatures = {}
        for signature in signatures:
            for key in list(itineraries_signatures.keys()):
                if signature[0] in key:
                    print(signature[0], 'found in', key, 'moving on')
                    continue
                elif key in signature[0]:
                    print(key, '\nfound in\n', signature[0], '\nkeep longer variant')
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
        #print(rtsig)
        for itsig in itineraries_signatures:
            #print(itsig)
            if route_signatures[rtsig]:
                cur = SequenceMatcher(None, route_signatures[rtsig], itsig).ratio()
                if cur > highest_score:
                    best_match = itsig
                    highest_score = cur
                if highest_score > 0.6:
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
                            try:
                                stop_ref = stop_data.stopidentfier
                            except AttributeError:
                                print('stopidentifier (ref) attribute not present in:',stop_data)
                                continue
                            stops_list.append(Stop(map_layer=self.map_layer,
                                                   primitive=osm.Node(map_layer=self.map_layer,
                                                                      tags={'name': stop_data.stopdescription,
                                                                            self.operator_specific_tags['ref']: stop_ref,
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
        print("Compare lines (route_master relations)")
        for line in self.lines:
            for route_member in self.lines[line].route_master.members:
                if route_member.id in self.map_layer.primitives['relations']:
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
