from scripts.Agency import Agency
import overpy
import os
from requests import post

use_test_data = False
download_again = True

#(._;<;);
# query = '''
# [out:xml][timeout:590];
# (
#   relation["operator"="De Lijn"];
# );
#
# (._;>>;);
# out meta;'''

query = '''
[out:xml][timeout:590];
(
  relation["operator"="De Lijn"]["ref"="600"];
);

(._;>>;);
out meta;'''

fn = os.path.join(os.path.split(os.getcwd())[0],'test_data', 'DeLijn.osm')

specific_tags = {}
for t in ['ref', 'route_ref', 'zone']:
    specific_tags[t] = t + ':De_Lijn'

delijn = Agency(name='De Lijn',
                operator_specific_tags=specific_tags)

if download_again:
    print('Downloading OSM data to file')
    response = post("http://overpass-api.de/api/interpreter", query)
    print(response)
    with open(fn, 'wb') as fh:
        fh.write(response.content)

api = overpy.Overpass()
if use_test_data:
    print("reading OSM file")
    with open(fn) as fh:
        osm_data = api.parse_xml(data=fh.read(),
                                 encoding='utf-8',
                                 parser=None)
else:
    print("downloading data directly from Overpass API")
    osm_data = api.query(query)

delijn.process_query_result(osm_data)

delijn.fetch_agency_data(
    sheet_url="https://docs.google.com/spreadsheet/ccc?key=1PGgEqobO90Mf9NsJHO1-JD-Npte1fYztK30HO5lRDI8&output=xls")
delijn.load_agency_data()
delijn.update_using_operator_data()
delijn.send_to_josm()
