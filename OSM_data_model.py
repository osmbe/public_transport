#!/bin/python
import OSM_lib as osmlib


class MapLayer():
    def __init__(self):
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.edges = {}
        self.changed = []  # list of all 'dirty' objects that need to be flagged for upload

    def as_xml(self, upload=False, generator='Python script'):
        params = {}
        if upload is False:
            params["upload"] = " upload='false'"
        else:
            params["upload"] = ""
        if generator:
            params["generator"] = " generator='{}'".format(generator)
        else:
            params["generator"] = ""
        xml = '''<?xml version='1.0' encoding='UTF-8'?>\n<osm version='0.6'{upload}{generator}>\n'''.format(**params)

        for n in self.nodes:
            xml += self.nodes[n].as_xml()
        for w in self.ways:
            xml += self.ways[w].as_xml()
        for r in self.relations:
            xml += self.relations[r].as_xml()

        xml += '''\n</osm>'''
        return xml


class Primitive:
    """Base class with common functionality between Nodes, Ways and Relations"""
    counter = -10000

    def __init__(self, ml, primitive, attributes=None, tags=None):
        self.maplayer = ml
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = {}
        if tags:
            self.tags = tags
        else:
            self.tags = {}
        self.primitive = primitive

        self.xml = ''
        self.dirty = False

        if not self.attributes or not ('id' in self.attributes):
            print(Primitive.counter)
            self.attributes['action'] = 'modify'
            self.attributes['visible'] = 'true'
            self.attributes['id'] = str(Primitive.counter)
            Primitive.counter -= 1

    def __repr__(self):
        r = '\n' + self.primitive + '\n'
        for key in self.attributes:
            r += "{}: {},  ".format(key, self.attributes[key])
        for key in self.tags:
            r += "{}: {}\n".format(key, self.tags[key])
        return r

    def add_tags(self, tags):
        if tags:
            for key in tags:
                self.add_tag(key, tags[key])

    def add_tag(self, key, value):
        self.tags[key] = value

    def as_xml(self, body=''):
        self.xml = '\n<{} '.format(self.primitive)
        for attr in ['id', 'lat', 'lon', 'action', 'timestamp', 'uid', 'user', 'visible', 'version', 'changeset']:
            if attr in self.attributes:
                if attr == 'timestamp':
                    self.attributes[attr] = str(self.attributes[attr]).replace(' ', 'T') + 'Z'
                if attr == 'user':
                    self.attributes[attr] = osmlib.xmlsafe(self.attributes[attr])
                self.xml += "{}='{}' ".format(attr, str(self.attributes[attr]))
        self.xml += '>'
        if body:
            self.xml += body
        for key in self.tags:
            self.xml += "\n  <tag k='{key}' v='{tag}' />".format(key=key, tag=osmlib.xmlsafe(self.tags[key]))
        self.xml += '\n</{}>'.format(self.primitive)
        return self.xml

    def get_parents(self):
        parents = []
        for way in self.maplayer.ways:
            if self.attributes['id'] in way.get_nodes():
                parents.append(way)
        for relation in self.maplayer.relations:
            if self.attributes['id'] in relation.get_members():
                parents.append(relation)
        return parents


class Node(Primitive):
    def __init__(self, ml, attributes=None, tags=None):
        if not attributes:
            attributes = {'lon': '0.0', 'lat': '0.0'}

        super().__init__(ml, primitive='node', attributes=attributes, tags=tags)
        ml.nodes[self.attributes['id']] = self


class Way(Primitive):
    def __init__(self, ml, attributes=None, nodes=None, tags=None):
        """Ways are built up as an ordered sequence of nodes
           it can happen we only know the id of the node,
           or we might have a Node object with all the details"""
        super().__init__(ml, primitive='way', attributes=attributes, tags=tags)

        self.nodes = []
        if nodes:
            self.add_nodes(nodes)
        ml.ways[self.attributes['id']] = self
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

    def add_nodes(self, nodes):
        for n in nodes:
            self.add_node(n)
        self.is_closed()

    def add_node(self, node):
        try:
            ''' did we receive an object instance to work with? '''
            n = node.attributes['id']
        except KeyError:
            ''' we received a string '''
            n = node
        self.nodes.append(str(n))

    def as_xml(self, body=''):
        for node in self.nodes:
            body += "\n  <nd ref='{node_id}' />".format(node_id=node)
        return super().as_xml(body=body)

    def is_closed(self):
        self.closed = False
        if self.nodes[0] == self.nodes[-1]:
            self.closed = True


class RelationMember:
    def __init__(self, role='', primtype='', member=None):
        self.primtype = primtype
        if role is None:
            self.role = ''
        else:
            self.role = role
        try:
            m = member.strip()
        except:
            try:
                ''' did we receive an object instance to work with? '''
                m = member.attributes['id']
                self.primtype = member.primitive
            except (KeyError, NameError):
                ''' the member id was passed as a string or an integer '''
                m = member
        self.memberid = str(m)

    def as_xml(self):
        return "\n  <member type='{primtype}' ref='{ref}' role='{role}' />".format(
            primtype=self.primtype, ref=self.memberid, role=self.role)


class Relation(Primitive):
    def __init__(self, ml, members=None, tags=None, attributes=None):
        super().__init__(ml, primitive='relation', attributes=attributes, tags=tags)

        if not members:
            self.members = []
        else:
            self.members = members

        ml.relations[self.attributes['id']] = self
        self.incomplete = None  # not all members are downloaded

    def __repr__(self):
        r = super().__repr__()
        return r

    def add_members(self, members):
        if members:
            for m in members:
                self.add_member(m)

    def add_member(self, member):
        print("adding".format(member))
        self.members.append(member)

    def as_xml(self, body=''):
        for member in self.members:
            body += member.as_xml()

        return super().as_xml(body=body)


class PublicTransportStop(Node):
    """"In this model a public transport stop is always mapped on a node with public_transport=platform tag

       This is a simplification, which makes sure there are always coordinates. In most cases this node
       represents the pole to which the flag with all details for the stop is mounted"""

    def __init__(self, ml, attributes=None, tags=None):
        super().__init__(ml, attributes, tags)
        if tags is None:
            self.tags['highway'] = 'bus_stop'
            self.tags['public_transport'] = 'platform'


class PublicTransportStopArea(Relation):
    pass


class PublicTransportRoute(Relation):
    """This is what we think of as a variation of a line"""

    def __init__(self, ml, members = None, tags = None, attributes = None):
        self.members = members
        tags['type'] = 'route'
        print('attr PT route: ', attributes)
        super().__init__(ml, members = members, attributes = attributes, tags = tags)
        self.continuous = None

    def is_continuous(self):
        last_node_of_previous_way = None
        for member in self.members:
            if member.primitive == 'way':
                ''' Is this way present in the downloaded data?'''
                if not (member.memberid in self.maplayer.ways):
                    self.continuous = None
                    return None
                ''' First time in loop, just store last node of way as previous node'''
                if last_node_of_previous_way is None:
                    last_node_of_previous_way = self.maplayer.ways[member.memberid][-1]
                    continue
                else:
                    if last_node_of_previous_way != self.maplayer.ways[member.memberid][0]:
                        self.continuous = False
                        return False
        '''If we get here, the route is continuous'''
        self.continuous = True
        return True


class PublicTransportRouteMaster(Relation):
    """This is what we think of as a public transport line
       It contains route relations for each variation of an itinerary"""

    def __init__(self, ml, members=None, tags=None, attributes=None):
        if members is None:
            self.members = []
        else:
            self.members = members
        if tags is None:
            self.tags = []
        else:
            self.tags = tags
        self.tags['type'] = 'route_master'
        super().__init__(ml, attributes=attributes, tags=self.tags)

    def add_route(self, route):
        super().add_member(RelationMember(primtype='relation', role='', member=route))


class Edge:
    """An edge is a sequence of ways that are connected to one another, they can either be between where highways fork,
       or where PT routes fork. An edge can contain shorter edges"""

    def __init__(self, ml, parts=None):
        self.parts = []
        if parts:
            self.parts = self.add_parts(parts)
        # ml.edges[self.attributes['id']] = self

    def add_parts(self, parts):
        for p in parts:
            self.add_part(p)

    def add_part(self, part):
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


'''
ml = MapLayer()
n1 = Node(ml)
n2 = Node(ml)
n3 = Node(ml)
n4 = Node(ml)
n5 = Node(ml)
n6 = Node(ml)
n7 = Node(ml)
n8 = Node(ml)

w1 = Way(ml, nodes = [n1, n2])
print(w1.asXML())
w2 = Way(ml, nodes = [n2, n3, n4])
w3 = Way(ml, nodes = [n4, n5])
w4 = Way(ml, nodes = [n5, n6])
w5 = Way(ml, nodes = [n6, n7])
w6 = Way(ml, nodes = [n7, n8])
print(w6.asXML())

e1 = Edge(ml, parts = [w1, w2])
e2 = Edge(ml, parts = [w3])
e3 = Edge(ml, parts = [w4, w5])
e4 = Edge(ml, parts = [w6])

print(e1.getWays())
print(e2.getWays())
print(e3.getWays())
print(e4.getWays())
'''
