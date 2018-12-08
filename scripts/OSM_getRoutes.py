import overpy
import sys

import OSM_data_model as osm

params = {'timeout': '325'}
operator = "De Lijn"
network = "DLLi"

if operator:
    params['operator'] = '["operator"~"' + operator + '"]'
else:
    params['operator'] = ''
if network:
    params['network'] = '["network"~"' + network + '"]'
else:
    params['network'] = ''

query = '''[out:xml][timeout:{timeout}];
(
  (
    node
      ["highway"="bus_stop"]{operator}{network};
    node
      ["railway"="tram_stop"]{operator}{network};
    node
      ["public_transport"="platform"]{operator}{network};
  )->.stop_nodes;
  node(around.stop_nodes:30)["amenity"="shelter"];
  way(around.stop_nodes:30)["amenity"="shelter"];

  relation["route"="bus"]{operator}{network};
);
(._;>;);

out meta;'''.format(**params)

print('============================================')
print(query)
print()
print('============================================')
print('Performing Overpass query, please be patient')
print('============================================')
sys.stdout.flush()

#  api = overpy.Overpass(url='https://overpass.kumi.systems/api/interpreter')
api = overpy.Overpass()

try:
    result = api.query(query)
except overpy.exception.OverpassBadRequest as e:
    print(e)

print('Data downloaded')

ml = osm.MapLayer()

for node in result.nodes:
    attributes = node.attributes
    attributes['id'] = node.id
    attributes['lon'] = node.lon
    attributes['lat'] = node.lat
    if node.tags.get('highway') == 'bus_stop':
        stop = osm.PublicTransportStop(ml, attributes=attributes, tags=node.tags)
    else:
        n = osm.Node(ml, attributes=attributes, tags=node.tags)

for way in result.ways:
    attributes = way.attributes
    attributes['id'] = way.id
    w = osm.Way(ml, attributes=attributes, tags=way.tags, nodes=way.nodes)

print(len(result.relations))
for relation in result.relations:
    attributes = relation.attributes
    attributes['id'] = relation.id
    members = []

    for rm in relation.members:
        members.append(osm.RelationMember(role=rm.role, primtype=rm._type_value, member=str(rm.ref)))
    PT_modes = ['bus', 'trolleybus', 'coach', 'tram', 'metro', 'train']
    type = relation.tags.get('type')
    route = relation.tags.get('route')
    route_master = relation.tags.get('route_master')
    if type == 'route':
        if route in PT_modes:
            r = osm.PublicTransportRoute(ml, attributes=attributes, tags=relation.tags, members=members)
    elif relation.tags.get('type') == 'route_master':
        if route_master in PT_modes:
            r = osm.PublicTransportRouteMaster(ml, attributes=attributes, tags=relation.tags, members=members)
    else:
        r = osm.Relation(ml, attributes=attributes, tags=relation.tags, members=members)

print (ml.url(layer_name='De Lijn 1305'))

#with open('test.osm', 'w') as fh:
#    fh.write(ml.xml(output='doc'))

print('Data saved to file')
