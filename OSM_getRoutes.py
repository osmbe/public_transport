import sys, overpy
import OSM_data_model as osm

params = {'timeout': '325'}
operator = "De Lijn"
network = "DLVB"

if operator: params['operator'] = '["operator"~"' + operator + '"]'
if network: params['network'] = '["network"~"' + network + '"]'
query='''[out:xml][timeout:{timeout}];
(
  //(
    //node
      //["highway"="bus_stop"]{operator}{network};
    //way
      //["amenity"="shelter"]["shelter_type"="public_transport";
    //node
    //  ["railway"="tram_stop"]{operator}{network};
    //node
    //  ["public_transport"="platform"]{operator}{network};
  //);
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

overpass_url = None # https://overpass.kumi.systems/api/interpreter'
api = overpy.Overpass(url=overpass_url)

result = api.query(query)

print('Data downloaded')

ml = osm.MapLayer()

for node in result.nodes:
    attributes = node.attributes
    attributes['id'] = node.id
    attributes['lon'] = node.lon
    attributes['lat'] = node.lat
    if node.tags.get('highway') == 'bus_stop':
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

print(len(result.relations))
for relation in result.relations:
    attributes = relation.attributes
    attributes['id'] = relation.id
    members = []

    for rm in relation.members:
        members.append(osm.RelationMember(role=rm.role, primtype=rm._type_value, member=str(rm.ref)))

    r=osm.Relation(ml, attributes=attributes, tags=relation.tags, members=members)
    print(r)

with open('test.osm','w') as fh:
    fh.write(ml.asXML())

print('Data saved to file')
