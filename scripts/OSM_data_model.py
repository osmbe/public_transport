#!/bin/python3
from typing import List, Dict, Any
from urllib.parse import urlencode
import xml.etree.ElementTree as eT

public_transport_mode_of_transport = ['bus', 'coach', 'trolleybus',
                                      'tram', 'subway', 'train']
suitable_for = {'bus': {'highway': ['motorway',
                                    'trunk',
                                    'primary',
                                    'secondary',
                                    'tertiary',
                                    'unclassified',
                                    'residential',
                                    'service',
                                    ],
                        'bus': ['yes', 'designated'],
                        'psv': ['yes', 'designated'],
                        },
                'coach': {'highway': ['motorway',
                                      'trunk',
                                      'primary',
                                      'secondary',
                                      'tertiary',
                                      'unclassified',
                                      'residential',
                                      'service',
                                      ],
                          },
                'trolleybus': {'trolley_wire': 'yes'
                               },
                'tram': {'railway': ['tram'],
                         },
                'subway': {'railway': ['subway'],
                           },
                'train': {'railway': ['rail']
                          },
                }


class MapLayer:
    primitives = {'nodes': {},
                  'ways': {},
                  'relations': {}
                  }

    def __init__(self, right_hand_side_traffic=True):
        """

        :type right_hand_side_traffic: bool
        """
        self.only_include_modified=True
        self.edges = {}
        self.stop_right_from_way = {}  # {way_id: [Stop, Stop, ...]}
        self.stop_left_from_way = {}  # {way_id: [Stop, Stop, ...]}
        self.right_hand_side_traffic = right_hand_side_traffic

    def get_primitive(self, primitive):
        prim = primitive[0]  # type: str
        primitive_id = primitive[1:]  # type: str
        if prim == 'n':
            if primitive_id in self.primitives['nodes']:
                return self.primitives['nodes'][primitive_id]
            else:
                raise ValueError('id ' + primitive_id + ' not found in nodes')
        elif prim == 'w':
            if primitive_id in self.primitives['nodes']:
                return self.primitives['ways'][primitive_id]
            else:
                raise ValueError('id ' + primitive_id + ' not found in ways')
        elif prim == 'r':
            if primitive_id in self.primitives['nodes']:
                return self.primitives['relations'][primitive_id]
            else:
                raise ValueError('id ' + primitive_id + ' not found in relations')
        else:
            raise ValueError('id should start with n, w or r')

    def from_overpy(self, osm_data):
        """For all nodes, ways and relations in the data downloaded using overpy
           add them to our map_layer instance and additionally create
           Stop, Itinerary and Line instances for them, if applicable"""
        print("Reading nodes")
        for node in osm_data.nodes:
            node.attributes['id'] = str(node.id)
            node.attributes['lon'] = node.lon
            node.attributes['lat'] = node.lat
            Stop(map_layer=self, primitive=Node(map_layer=self,
                                                attributes=node.attributes,
                                                tags=node.tags))

        print("Reading ways")
        for way in osm_data.ways:
            way.attributes['id'] = str(way.id)
            Stop(map_layer=self, primitive=Way(map_layer=self,
                                               attributes=way.attributes,
                                               tags=way.tags,
                                               nodes=way.nodes))

        print("Reading relations")
        for rel in osm_data.relations:
            members = []
            for member in rel.members:
                members.append(RelationMember(member=str(member.ref),
                                              role=member.role,
                                              primitive_type=member._type_value)
                               )
            rel.attributes['id'] = str(rel.id)

            rltn = Relation(map_layer=self,
                            attributes=rel.attributes,
                            tags=rel.tags,
                            members=members)

            if 'type' in rel.tags:
                if rel.tags['type'] == 'route':
                    if 'route' in rel.tags:
                        if rel.tags['route'] in public_transport_mode_of_transport:
                            Itinerary(map_layer=self, route_relation=rltn)

                elif rel.tags['type'] == 'route_master':
                    Line(map_layer=self, route_master_relation=rltn)

    def xml(self, upload='false', generator='', only_include_modified=True):
        """
        :param only_include_modified: bool
        :type upload: str
        :type generator: string documentation to be added to OSM xml file for tool that generated the XML data
        """
        print("Generating XML")
        self.only_include_modified=only_include_modified
        assert isinstance(upload, str), "upload is not a string: %r" % upload
        xml_attributes = {'version': '0.6', 'upload': upload}

        assert isinstance(generator, str), "generator is not a string: %r" % generator
        if generator:
            xml_attributes['generator'] = generator
        osm_xml_root = eT.Element('osm', attrib=xml_attributes)

        for primtype in ('nodes', 'ways', 'relations'):
            for prim_id in self.primitives[primtype]:
                xml = self.primitives[primtype][prim_id].xml
                osm_xml_root.extend([xml])
        return eT.ElementTree(element=osm_xml_root)

    def url(self, upload='false', generator='', new_layer=True, layer_name=''):
        """
        :type upload: str
        :type generator: string documentation to be added to OSM xml file for tool that generated the XML data
        :type new_layer: bool set to False to add data to currently open layer in JOSM
        :type layer_name: string name for the layer to be created if new_layer=True
        """
        values = {'data': eT.tostring(self.xml(upload=upload,
                                               generator=generator),
                                      encoding='UTF-8'
                                      ).decode('UTF-8')
                  }
        if new_layer is False:
            values['new_layer'] = 'false'
        else:
            values['new_layer'] = 'true'

        if layer_name:
            values['layer_name'] = layer_name

        return "http://localhost:8111/load_data?" + urlencode(values)

    def http_link(self, upload='false', generator='',
                  new_layer=True, layer_name='', link_text=''):
        """
        :type upload: str
        :type generator: string documentation to be added to OSM xml file for tool that generated the XML data
        :type new_layer: bool set to False to add data to currently open layer in JOSM
        :type layer_name: string name for the layer to be created if new_layer=True
        :type link_text: string text to show on the link
        """
        params = {'link_text': link_text,
                  'url': self.url(upload=upload,
                                  generator=generator,
                                  new_layer=new_layer,
                                  layer_name=layer_name)
                  }
        return '<a href="{url}">{link_text}</a>'.format(**params)


class Primitive:
    """Base class with common functionality between Nodes, Ways and Relations"""
    counter = -10000
    _parent_ways = {}
    _parent_relations = {}

    def __init__(self, map_layer, primitive, attributes=None, tags=None):
        self.maplayer = map_layer

        if attributes:
            self.attributes = attributes
        else:
            self.attributes = {}
        if tags:
            self.tags = tags
        else:
            self.tags = {}
        self.primitive = primitive

        if not ('id' in self.attributes):
            self.modified = True
            self.attributes['visible'] = 'true'
            self.attributes['id'] = str(Primitive.counter)
            Primitive.counter -= 1

    def __repr__(self):
        r = '\n' + self.primitive + '\n'
        for key in self.attributes:
            r += "{}: {},  ".format(key, self.attributes[key])
        for key in self.tags:
            r += "\n{}: {}".format(key, self.tags[key])
        return r

    @property
    def id(self):
        return self.attributes['id']

    @id.setter
    def id(self, new_id):
        self.attributes['id'] = new_id

    @property
    def modified(self):
        if 'action' in self.attributes:
            return self.attributes['action'] == 'modify'
        else:
            return False

    @modified.setter
    def modified(self, modified_flag):
        if modified_flag:
            self.attributes['action'] = 'modify'

    def add_tags(self, tags, mark_modified=True):
        """
       :type mark_modified: bool
        """
        if tags:
            for key in tags:
                self.add_tag(key, tags[key], mark_modified=mark_modified)

    def add_tag(self, key, value, mark_modified=True):
        """
        :type key str
        :type value str
        :type mark_modified: bool
        """
        self.tags[key] = value
        if mark_modified:
            self.modified = True

    @property
    def xml(self):
        if self.maplayer.only_include_modified:
            # Check if primitive itself is modified
            if ('action' in self.attributes and
                    not self.attributes['action'] == 'modify'):
                # if it isn't check its parents and grandparents
                parent_modified = False
                grand_parent_modified = False
                for p in self.get_parents:
                    if ('action' in p.attributes
                            and p.attributes['action'] == 'modify'):
                        parent_modified = True
                        break
                    for gp in p.get_parents:
                        if ('action' in gp.attributes
                                and gp.attributes['action'] == 'modify'):
                            grand_parent_modified = True
                            break
                    if grand_parent_modified: break
                if not (parent_modified or
                        grand_parent_modified):
                    return ''
        xml_attributes = {}
        for attr in self.attributes:
            assert isinstance(attr, str), "attr is not a string: %r" % attr
            if attr == 'timestamp':
                xml_attributes['timestamp'] = str(self.attributes['timestamp']).replace(' ', 'T').replace('Z', '') + 'Z'
            elif self.attributes[attr] is not None:
                xml_attributes[attr] = str(self.attributes[attr])
        _xml = eT.Element(self.primitive, attrib=xml_attributes)
        for key in self.tags:
            assert isinstance(key, str), "key is not a string: %r" % key
            if str(self.tags[key]) is not None:
                _xml.extend([eT.Element('tag', attrib={'k': key,
                                                       'v': str(self.tags[key])
                                                       }
                                        )
                             ])
        return _xml

    @property
    def get_parents(self):
        parents = []
        if self.id in self._parent_ways:
            parents.append(self._parent_ways[self.id])
        if self.id in self._parent_relations:
            parents.append(self._parent_relations[self.id])
        return parents

    @property
    def get_parent_ways(self):
        if self.id in self._parent_ways:
            return self._parent_ways[self.id]
        else:
            self._parent_ways[self.id] = []
            for way in self.maplayer.primitives['ways']:
                if self.id in way.get_nodes():
                    self._parent_ways[self.id].append(way)
            return self._parent_ways[self.id]

    @property
    def get_parent_relations(self):
        if self.id in self._parent_relations:
            return self._parent_relations[self.id]
        else:
            self._parent_relations[self.id] = []
            for relation in self.maplayer.primitives['relations']:
                if self.id in relation.get_members():
                    self._parent_relations[self.id].append(relation)
            return self._parent_relations[self.id]


class Node(Primitive):
    def __init__(self, map_layer, attributes=None, tags=None):
        if not attributes:
            attributes = {'lon': '0.0', 'lat': '0.0'}

        super().__init__(map_layer, primitive='node', attributes=attributes, tags=tags)
        map_layer.primitives['nodes'][self.attributes['id']] = self


class Way(Primitive):
    def __init__(self, map_layer, attributes=None, nodes=None, tags=None):
        """Ways are built up as an ordered sequence of nodes
           it can happen we only know the id of the node,
           or we might have a Node object with all the details"""
        super().__init__(map_layer, primitive='way', attributes=attributes, tags=tags)

        self.nodes = []
        if nodes:
            self.add_nodes(nodes, mark_modified=False)
        map_layer.primitives['ways'][self.attributes['id']] = self
        self.closed = None
        self.incomplete = None  # not all nodes are downloaded

    def __repr__(self):
        body = super().__repr__()
        for node in self.nodes:
            body += "\n  {node_id}".format(node_id=node)
        return body

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, position):
        return self.nodes[position]

    def add_nodes(self, nodes, mark_modified=True):
        for n in nodes:
            self.add_node(n, mark_modified)
        self.is_closed()

    def add_node(self, node, mark_modified=True):
        try:
            """ did we receive an object instance to work with? """
            n = node.attributes['id']
        except KeyError:
            """ we received a string """
            n = node
        self.nodes.append(str(n))
        if mark_modified:
            self.modified = True

    @property
    def xml(self):
        way = super().xml  # type: eT.Element
        for nd in self.nodes:
            assert isinstance(nd, str), "nd is not a string: %r" % nd
            if nd is not None:
                way.extend([eT.Element('nd', attrib={'ref': str(nd)}
                                       )
                            ])
        return way

    def is_closed(self):
        self.closed = False
        if self.nodes[0] == self.nodes[-1]:
            self.closed = True


class RelationMember(object):
    _instances = {}

    def __new__(cls, *args, **kwargs):
        member = kwargs['member']
        if 'primitive_type' in kwargs:
            primitive_type = kwargs['primitive_type']
        else:
            if isinstance(member, Node):
                primitive_type = 'node'
            elif isinstance(member, Way):
                primitive_type = 'way'
            elif isinstance(member, Relation):
                primitive_type = 'relation'
            else:
                raise ValueError("primitive's type can't be determined")
        if 'role' in kwargs:
            role = kwargs['role']
        else:
            role = ''
        if isinstance(member, Primitive):
            member_id = member.id
        elif isinstance(member, str):
            member_id = member.strip()
        else:
            member_id = str(member)
        key = (role, primitive_type[0], member_id)
        if key in cls._instances:
            return cls._instances[key]
        else:
            instance = object.__new__(cls)
            cls._instances[key] = instance
            return instance

    def __init__(self, member, role="", primitive_type=""):
        """
        :type role: str
        :type primitive_type: str
        :type member [Primitive, str, int]
        """
        if role is None:
            self.role = ""
        else:
            self.role = role
        self.primitive = None

        if isinstance(member, Primitive):
            self.id = member.id
            self.primitive = member
        elif isinstance(member, str):
            self.id = member.strip()
        elif isinstance(member, int):
            self.id = str(member)
        else:
            raise ValueError("The id should either come from the primitive or be passed as a parameter")

        if self.primitive:
            self.primitive_type = member.primitive
        elif primitive_type:
            self.primitive_type = primitive_type
        else:
            raise ValueError(
                "It should either be possible to infer the primitive's type from member, or passed as a parameter")

    @property
    def xml(self):
        assert isinstance(self.primitive_type, str), "self.primitive_type is not a string: %r" % self.primitive_type
        assert isinstance(self.id, str), "self.id is not a string: %r" % self.id
        assert isinstance(self.role, str), "self.role is not a string: %r" % self.role
        return eT.Element('member', attrib={'type': self.primitive_type,
                                            'ref': self.id,
                                            'role': self.role})


class Relation(Primitive):
    def __init__(self, map_layer, members=None, tags=None, attributes=None):
        super().__init__(map_layer, primitive='relation', attributes=attributes, tags=tags)

        if not members:
            self.members = []
        else:
            self.members = members

        map_layer.primitives['relations'][self.attributes['id']] = self
        self.incomplete = None  # not all members are downloaded

    def __repr__(self):
        r = ''
        for member in self.members:
            r += member.__repr__()

        return r + super().__repr__()

    def add_members(self, members, mark_modified=True):
        if members:
            for m in members:
                self.add_member(m, mark_modified)

    def add_member(self, member, mark_modified=True):
        assert isinstance(member, RelationMember)
        self.members.append(member)
        if mark_modified:
            self.modified = True

    @property
    def xml(self):
        rel = super().xml
        for member in self.members:
            assert isinstance(member.xml, eT.Element), "member.xml is not an element: %r" % member.xml
            rel.extend([member.xml])

        return rel


class Stop:
    """Stops can consist of just a platform node, or a stop_position,
       or a stop_position combined with a platform node or way."""
    lookup = {}  # type: Dict[str, Stop]

    def __init__(self, map_layer, primitive=None):
        """
        :type map_layer: MapLayer
        :type primitive: Primitive
        """
        self.map_layer = map_layer
        self.stop_position_node = None
        self.platform_node = None
        self.platform_way = None

        # the highway just before and just after the stop.
        # If the way is not split near the stop, there is just a single item in the list
        # If the way is split, the list has 2 items
        self.adjacent_ways = [None]

        if isinstance(primitive, Primitive):
            self.add(primitive)

    def add(self, primitive):
        """ This method accepts both Node, Way and RelationMember instances
            It analyses them and assigns them to the proper attribute
            as a RelationMember
            :type primitive: Primitive"""
        pt_tag = "public_transport" in primitive.tags
        hw_tag = "highway" in primitive.tags
        rw_tag = 'railway' in primitive.tags
        if isinstance(primitive, RelationMember):
            if isinstance(primitive.primitive, Node):
                # It would be better to look at whether this node is a way
                # node of a highway suitable for the mode of transport
                pt_tag = "public_transport" in primitive.primitive.tags
                hw_tag = "highway" in primitive.primitive.tags
                rw_tag = "railway" in primitive.primitive.tags
                if (pt_tag and primitive.primitive.tags['public_transport'] == 'platform' or
                        hw_tag and primitive.primitive.tags['highway'] == 'bus_stop' or
                        rw_tag and primitive.primitive.tags['railway'] == 'tram_stop'):
                    self.platform_node = primitive
                    self.lookup[primitive.primitive.id] = self
                elif (pt_tag and primitive.primitive.tags['public_transport'] == 'stop_position'):
                    self.stop_position_node = primitive
                    self.lookup[primitive.primitive.id] = self
            if isinstance(primitive.primitive, Way):
                if pt_tag and primitive.primitive.tags['public_transport'] == 'platform':
                    self.platform_way = primitive
                    self.lookup[primitive.primitive.id] = self

        elif isinstance(primitive, Node):
            if (pt_tag and primitive.tags['public_transport'] == 'platform' or
                    hw_tag and primitive.tags['highway'] == 'bus_stop'):
                self.platform_node = RelationMember(role='platform',
                                                    primitive_type='node',
                                                    member=primitive)
                self.lookup[primitive.id] = self
            elif pt_tag and primitive.tags['public_transport'] == 'stop_position':
                self.stop_position_node = RelationMember(role='stop',
                                                         primitive_type='node',
                                                         member=primitive)
                self.lookup[primitive.id] = self
            elif hw_tag and primitive.tags['highway'] == 'bus_stop':
                if primitive.get_parent_ways in suitable_for['bus']['highway']:
                    self.stop_position_node = RelationMember(role='stop',
                                                             primitive_type='node',
                                                             member=primitive)
                    self.lookup[primitive.id] = self
                else:
                    self.platform_node = RelationMember(role='platform',
                                                        primitive_type='node',
                                                        member=primitive)
                    self.lookup[primitive.id] = self

        elif isinstance(primitive, Way):
            if (pt_tag and primitive.tags['public_transport'] == 'platform' or
                    hw_tag and primitive.tags['highway'] == 'platform' or
                    rw_tag and primitive.tags['railway'] == 'platform'):
                self.platform_way = RelationMember(role='platform',
                                                   primitive_type='way',
                                                   member=primitive)
                self.lookup[primitive.id] = self

    @property
    def get_stop_primitives(self):
        result = []  # type: List[RelationMember]
        for o in [self.stop_position_node, self.platform_node, self.platform_way]:
            if o:
                assert isinstance(o, RelationMember)
                result.append(o)
        return result


class StopArea:
    pass


class Itinerary:
    """An ordered sequence of stops along an itinerary.

       In OpenStreetMap it is mapped as a route relation"""
    lookup = {}  # type: Dict[str, Itinerary]

    def __init__(self, map_layer, route_relation=None, mode_of_transport='bus',
                 stops=None, ways=None, extra_tags=None):
        """Either  there is a route relation, or one will be created based on the values in
           stops, ways and extra_tags.
           :type map_layer: MapLayer
           :type stops: List[Stop]
           :type ways:  List[Way]"""
        self.map_layer = map_layer
        self.others = []
        if stops is None:
            self.stops = []
        else:
            self.stops = stops

        if ways is None:
            self.ways = []
        else:
            self.ways = ways

        if extra_tags is None:
            tags = {}
        else:
            tags = extra_tags

        self.mode_of_transport = mode_of_transport

        if route_relation is None:
            tags['type'] = 'route'
            tags['route'] = self.mode_of_transport
            tags['public_transport:version'] = '2'

            members = []
            for stop in self.stops:
                members.append(stop)
            for way in self.ways:
                members.append(RelationMember(way))
            self.route = Relation(map_layer,
                                  members=members,
                                  tags=tags)
        else:
            self.route = route_relation
            self.mode_of_transport = self.route.tags['route']
            self.inventorise_members()

        self.lookup[self.route.id] = self

    def __repr__(self):
        return "<{0}.{1}(mode_of_transport={2}, route={3})>".format(
            self.__module__, type(self).__name__, self.mode_of_transport, self.route)

    def __str__(self):
        _str = "\n"
        for s in self.stops:
            for st in s.get_stop_primitives:
                _str += ", " + st.role + ' ' + st.primitive_type + ' ' + st.id
                if st.primitive:
                    _str += "\n" + str(st.primitive.tags)
        return self.__repr__() + _str

    def inventorise_members(self):
        # split route relation members into stops, ways and other objects
        self.stops = []
        self.ways = []
        self.others = []
        for member in self.route.members:
            if member.primitive_type == 'node':
                node = self.route.maplayer.primitives['nodes'][member.id]  # type: Node
                hw_tag = 'highway' in node.tags
                rw_tag = 'railway' in node.tags
                pt_tag = 'public_transport' in node.tags
                if (hw_tag and node.tags['highway'] == 'bus_stop' or
                        rw_tag and node.tags['railway'] == 'tram_stop' or
                        pt_tag and node.tags['public_transport'] in ['platform', 'stop_position']):
                    self.stops.append(Stop.lookup[member.id])
                else:
                    self.others.append(member)
            elif member.primitive_type == 'way':
                way = self.route.maplayer.primitives['ways'][member.id]  # type: Way
                hw_tag = 'highway' in way.tags
                rw_tag = 'railway' in way.tags
                if (hw_tag and way.tags['highway'] == 'platform' or
                        rw_tag and way.tags['railway'] == 'platform'):
                    self.stops.append(member)
                else:
                    self.ways.append(member)
            else:
                self.others.append(member)

    def update_stops(self, new_stops_sequence):
        """

        :type new_stops_sequence: list[Stop]
        """
        if not self.stops:
            self.inventorise_members()
        self.stops = new_stops_sequence

        self.route.members = []  # type: List[RelationMember]
        for stop in self.stops:
            self.route.add_members(stop.get_stop_primitives)

        for way in self.ways:
            self.route.add_member(way)
        for other in self.others:
            self.route.members.append(other)

    @property
    def is_continuous(self) -> [bool, None]:
        last_node_of_previous_way = None
        for member in self.route.members:
            if member.primitive_type == 'way':
                """ Is this way present in the downloaded data?"""
                if not (member.id in self.route.maplayer.primitives['ways']):
                    return None
                """ First time in loop, just store last node of way as previous node"""
                if last_node_of_previous_way is None:
                    last_node_of_previous_way = self.route.maplayer.primitives['ways'][member.id][-1]
                    continue
                else:
                    if last_node_of_previous_way != self.route.maplayer.primitives['ways'][member.id][0]:
                        return False
        if last_node_of_previous_way:
            """If we get here, the route is continuous"""
            return True


class Line:
    """Collection of variations in itinerary.

       In OpenStreetMap it is mapped as a route_master relation"""
    lookup = {}  # type: Dict[str, Line]

    def __init__(self, map_layer, route_master_relation=None, mode_of_transport='bus', extra_tags=None):
        """:type map_layer: MapLayer
        """
        self.map_layer = map_layer
        self.mode_of_transport = mode_of_transport

        if extra_tags is None:
            tags = {}
        else:
            tags = extra_tags

        if isinstance(route_master_relation, Relation):
            if route_master_relation.tags['type'] == 'route_master':
                self.route_master = route_master_relation
                self.mode_of_transport = self.route_master.tags['route_master']
            else:
                raise ValueError("Only route_master relations should be added to a Line")
        else:
            tags['type'] = 'route_master'
            tags['route_master'] = self.mode_of_transport

            self.route_master = Relation(map_layer,
                                         tags=tags)

        self.lookup[self.route_master.id] = self

    def add_route(self, route_relation):
        self.route_master.add_member(RelationMember(role='',
                                                    primitive_type='relation',
                                                    member=route_relation.route))


class Edge:
    """An edge is a logical sequence of ways, they can either be the ways between where highways fork,
       or where routes fork. An edge can contain shorter edges"""

    def __init__(self, parts=None):
        self.parts = []
        if parts:
            self.add_parts(parts)

    def add_parts(self, parts: Way):
        for p in parts:
            self.add_part(p)

    def add_part(self, part: Way):
        self.parts.append(part)

    def get_ways(self):
        ways = []
        if self.parts:
            for p in self.parts:
                try:
                    p.get_nodes()
                    ways.append(p)
                except:
                    try:
                        ways.extend(p.get_ways())
                    except:
                        pass
        return ways


if __name__ == '__main__':
    ml = MapLayer()
    n1 = Node(ml)
    n2 = Node(ml)
    n3 = Node(ml)
    n4 = Node(ml)
    n5 = Node(ml)
    n6 = Node(ml)
    n7 = Node(ml)
    n8 = Node(ml)

    w1 = Way(ml, nodes=[n1, n2])
    print(eT.tostring(w1.xml, encoding='UTF-8'))
    w2 = Way(ml, nodes=[n2, n3, n4])
    w3 = Way(ml, nodes=[n4, n5])
    w4 = Way(ml, nodes=[n5, n6])
    w5 = Way(ml, nodes=[n6, n7])
    w6 = Way(ml, nodes=[n7, n8])
    print(eT.tostring(w6.xml, encoding='UTF-8'))
    """
    e1 = Edge(ml, parts=[w1, w2])
    e2 = Edge(ml, parts=[w3])
    e3 = Edge(ml, parts=[w4, w5])
    e4 = Edge(ml, parts=[w6])

    print(e1.get_ways())
    print(e2.get_ways())
    print(e3.get_ways())
    print(e4.get_ways())
    print(eT.tostring(ml.xml(), encoding='UTF-8'))
    """

    rm1 = RelationMember(role="", member=w1)

    platform_node1 = Node(ml, tags={'name': 'First halt',
                                    'ref': '123',
                                    'highway': 'bus_stop',
                                    }
                          )
    stop_position_node1 = Node(ml, tags={'name': 'First halt',
                                         'public_transport': 'stop_position',
                                         'bus': 'yes',
                                         }
                               )
    platform_node2 = Node(ml, tags={'name': 'Second halt',
                                    'ref': '125',
                                    'highway': 'bus_stop'
                                    }
                          )
    platform_node3 = Node(ml, tags={'name': 'Third halt',
                                    'ref': '127',
                                    'highway': 'bus_stop'
                                    }
                          )

    stop1 = Stop(ml, platform_node1)
    stop1a = Stop(ml, stop_position_node1)
    stop2 = Stop(ml, platform_node2)
    stop3 = Stop(ml, platform_node3)

    itn1 = Itinerary(ml, stops=[stop1, stop2, stop3], extra_tags={'ref:De_Lijn': '3303'}, mode_of_transport='bus')

    itn1.update_stops([stop3.platform_node, stop2.platform_node])
    print(stop1)
    print(stop1a)
