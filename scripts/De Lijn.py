from scripts.Agency import Agency
import overpy
import os

query = '''
[out:xml][timeout:90];
(
  relation["operator"="De Lijn"]["ref"="305"];
  node["operator"="De Lijn"];
);
(._;<;);
(._;>>;);
out meta;'''

specific_tags = {}
for t in ['ref', 'route_ref', 'zone']:
    specific_tags[t] = t + ':De_Lijn'

delijn = Agency(name='De Lijn',
                operator_specific_tags=specific_tags)
api = overpy.Overpass()
#osm_data = api.query(query)

with open(os.path.join(os.path.split(os.getcwd())[0],
                       'test_data', 'DeLijn1305.osm')) as fh:
    osm_data = api.parse_xml(data=fh.read(),
                             encoding='utf-8',
                             parser=None)

delijn.process_query_result(osm_data)

delijn.fetch_agency_data(
    sheet_url="https://docs.google.com/spreadsheet/ccc?key=1PGgEqobO90Mf9NsJHO1-JD-Npte1fYztK30HO5lRDI8&output=xls")
delijn.load_agency_data()
delijn.update_using_operator_data()
delijn.send_to_josm()
