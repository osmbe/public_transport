import sys, overpy
import OSM_data_model as osm

operator = network = ''

params = {'timeout': '325'}
operator="De Lijn"
network="DLVB"

if operator: params['operator'] = '["operator"~"' + operator + '"]'
if network: params['network'] = '["network"~"' + network + '"]'
query='''[out:xml][timeout:{timeout}];
(
  (
    node
      ["highway"="bus_stop"]{operator}{network};
    //node
    //  ["railway"="tram_stop"]{operator}{network};
    //node
    //  ["public_transport"="platform"]{operator}{network};
  );
  //._;<;
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

api = overpy.Overpass(url='https://overpass.kumi.systems/api/interpreter')

result = api.query(query)

print('Data downloaded')

ml = osm.MapLayer()

for node in result.nodes:
    attributes = node.attributes
    attributes['id'] = node.id
    attributes['lon'] = node.lon
    attributes['lat'] = node.lat
    if node.tags.get('highway')=='bus_stop':
        stop=osm.PT_Stop(ml, attributes=attributes, tags=node.tags)
        #print(stop.asXML())
    else:
        n=osm.Node(ml, attributes=attributes, tags=node.tags)
        #print(n.asXML())

for way in result.ways:
    attributes = way.attributes
    attributes['id'] = way.id
    #print(dir(way))
    w=osm.Way(ml, attributes=attributes, tags=way.tags, nodes=way.nodes)
    #print(w.asXML())

for relation in result.relations:
    attributes = relation.attributes
    attributes['id'] = relation.id
    members = []
    for rm in relation.members:
        print(rm.role, rm.ref)
        print(type(rm))
        print(rm['timestamp'], dir(rm['timestamp']))
        print(rm.timestamp, dir(rm.timestamp))
        members.append(osm.RelationMember(role=rm.role, primtype=type(rm), member=rm.ref))
        #print(dir(rel))
    #print(relation.members)
    r=osm.Relation(ml, attributes=attributes, tags=relation.tags, members=members)

with open('test.osm','w') as fh:
    fh.write(ml.asXML())

