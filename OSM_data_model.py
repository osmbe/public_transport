#!/bin/python
import OSM_lib as OL

class MapLayer():
    def __init__(self):
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        self.edges = {}
        self.changed = [] # list of all 'dirty' objects that need to be flagged for upload

    def asXML(self):
        params = {upload: " upload='false'",
                  generator: " generator='Python script'",
                  }
        xml = '''<?xml version='1.0' encoding='UTF-8'?>\n<osm version='0.6'{upload}{generator}>\n'''.format(**params)
        print (xml)
        for n in self.nodes:
            xml += self.nodes[n].asXML()
        for w in self.ways:
            xml += self.ways[w].asXML()
        for r in self.relations:
            xml += self.relations[r].asXML()

        xml += '''\n</osm>'''
        return xml


class OSM_Primitive():
    counter = -10000

    def __init__(self, ml, primitive, attributes=None, tags=None):
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = {}
        if tags:
            self.tags = tags
        else:
            self.tags = {}
        self.primitive = primitive

        self.dirty = False

        if not (self.attributes) or not ('id' in self.attributes):
            print(OSM_Primitive.counter)
            self.attributes['action'] = 'modify'
            self.attributes['visible'] = 'true'
            self.attributes['id'] = str(OSM_Primitive.counter)
            OSM_Primitive.counter -= 1

    def __repr__(self):
        r = '\n' + self.primitive + '\n'
        for key in self.attributes:
            r += "{}: {},  ".format(key, self.attributes[key])
        for key in self.tags:
            r += "{}: {}\n".format(key, self.tags[key])
        return r

    def addTags(self, tags):
        if tags:
            for key in tags:
                self.addTag(key, tags[key])

    def addTag(self, key, value):
        self.tags[key] = value

    def asXML(self, body=''):
        self.xml = '\n<{} '.format(self.primitive)
        for attr in ['id', 'lat', 'lon', 'action', 'timestamp', 'uid', 'user', 'visible', 'version', 'changeset']:
            if attr in self.attributes:
                if attr == 'timestamp':
                    self.attributes[attr] = str(self.attributes[attr]).replace(' ', 'T') + 'Z'
                if attr == 'user':
                    self.attributes[attr] = OL.xmlsafe(self.attributes[attr])
                self.xml += "{}='{}' ".format(attr, str(self.attributes[attr]))
        self.xml += '>'
        if body: self.xml += body
        for key in self.tags:
            self.xml += "\n  <tag k='{key}' v='{tag}' />".format(key=key, tag=OL.xmlsafe(self.tags[key]))
        self.xml += '\n</{}>'.format(self.primitive)
        return self.xml

    def getParents(self, ml):
        parents = []
        for way in ml.ways:
            if self['id'] in way.getNodes():
                parents.append(way)
        for relation in ml.relations:
            if self['id'] in relation.getMembers():
                parents.append(relation)
        return parents


class Node(OSM_Primitive):
    def __init__(self, ml, attributes=None, tags=None):
        if not (attributes):
            attributes = {'lon': '0.0', 'lat': '0.0'}

        super().__init__(ml, primitive='node', attributes=attributes, tags=tags)
        ml.nodes[self.attributes['id']] = self


class Way(OSM_Primitive):
    def __init__(self, ml, attributes=None, nodes=None, tags=None):
        '''Ways are built up as an ordered sequence of nodes
           it can happen we only know the id of the node,
           or we might have a Node object with all the details'''
        super().__init__(ml, primitive='way', attributes=attributes, tags=tags)
        self.nodes = []
        if nodes: self.addNodes(nodes)
        ml.ways[self.attributes['id']] = self
        self.closed = None
        self.incomplete = None # not all nodes are downloaded

    def __repr__(self):
        body = super().asXML()
        for node in self.nodes:
            body += "\n  {node_id}".format(node_id=node)
        return body

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, position):
        return self.nodes[position]

    def addNodes(self, nodes):
        if nodes:
            for n in nodes:
                self.addNode(n)
        self.isClosed()

    def addNode(self, node):
        try:
            ''' did we receive an object instance to work with? '''
            n = node.attributes['id']
        except KeyError:
            ''' we received a string '''
            n = node
        self.nodes.append(str(n))

    def asXML(self):
        body = ''
        for node in self.nodes:
            body += "\n  <nd ref='{node_id}' />".format(node_id=node)
        return super().asXML(body=body)

    def isClosed(self):
        self.clsoed = False
        if self.nodes[0] == self.nodes[-1]:
            self.closed = True


class RelationMember():
    def __init__(self, role='', primtype='', member=None):
        self.primtype = primtype
        if role == None:
            self.role=''
        else:
            self.role = role
        try:
            m = member.strip()
        except:
            try:
                ''' did we receive an object instance to work with? '''
                m = member.attributes['id']
                self.primtype = member.primitive
            except (KeyError, NameError) as e:
                ''' the member id was passed as a string or an integer '''
                m = member
        self.memberid = str(m)

    def asXML(self):
        return "\n  <member type='{primtype}' ref='{ref}' role='{role}' />".format(
            primtype=self.primtype, ref=self.memberid, role=self.role)


class Relation(OSM_Primitive):
    def __init__(self, ml, members=None, tags=None, attributes=None):
        super().__init__(ml, primitive='relation', attributes=attributes, tags=tags)

        if not members:
            self.members = []
        else:
            self.members = members

        ml.relations[self.attributes['id']] = self
        self.incomplete = None # not all members are downloaded

    def __repr__(self):
        r = super().__repr__()
        return r

    def addMembers(self, members):
        if members:
            for m in members:
                self.addMember(m)

    def addMember(self, member):
        self.members.append(member)

    def asXML(self):
        body = ''
        for member in self.members:
            body += member.asXML()

        return super().asXML(body=body)


class PT_Stop(Node):
    '''In this model a public transport stop is always mapped on a node with public_transport=platform tag
       This is a simplification, which makes sure there are always coordinates. In most cases this node
       represents the pole to which the flag with all details for the stop is mounted'''

    def __init__(self, ml, attributes=None, tags=None):
        super().__init__(ml, attributes, tags)
        if tags == None:
            self.tags['highway'] = 'bus_stop'
            self.tags['public_transport'] = 'platform'


class PT_StopArea(Relation):
    pass


class PT_Route(Relation):
    '''This is what we think of as a variation of a line'''

    def __init__(self, ml, members=None, tags=None, attributes=None):
        tags['type'] = 'route'
        print('attr PT route: ', attributes)
        super().__init__(ml, attributes=attributes, tags=tags)
        self.continuous = None

    def isContinuous(self):
        lastNodeOfPreviousWay = None
        for member in self.members:
            if member.primitive == 'way':
                ''' Is this way present in the downloaded data?'''
                if  not(member.memberid in ml.ways):
                    self.continuous = None
                    return None
                ''' First time in loop, just store last node of way as previous node'''
                if lastNodeOfPreviousWay == None:
                    lastNodeOfPreviousWay = ml.ways[member.memberid][-1]
                    continue
                else:
                    if lastNodeOfPreviousWay != ml.ways[member.memberid][0]:
                        self.continuous = False
                        return False
        '''If we get here, the route is continuous'''
        self.continuous = True
        return True

class PT_RouteMaster(Relation):
    '''This is what we think of as a public transport line
       It contains route relations for each variation of an itinerary'''

    def __init__(self, ml, members=None, tags=None, attributes=None):
        tags['type'] = 'route_master'
        super().__init__(ml, attributes=attributes, tags=tags)

    def addRoute(self, route):
        m = RelationMember(primtype='relation', role='', member=route)
        super().addMember(m)


class Edge():
    '''An edge is a sequence of ways that are connected to one another, they can either be between where highways fork,
       or where PT routes fork. An edge can contain shorter edges'''

    def __init__(self, ml, parts=None):
        self.parts = []
        if parts:
            self.parts = self.addParts(parts)
        # ml.edges[self.attributes['id']] = self

    def addParts(self, parts):
        for p in parts:
            self.addPart(p)

    def addPart(self, part):
        self.parts.append(part)

    def getWays(self):
        ways = []
        if self.parts:
            for p in self.parts:
                try:
                    p.getNodes()
                    ways.append(p)
                except:
                    try:
                        ways.extend(p.getWays())
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
