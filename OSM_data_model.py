#!/bin/python

class MapLayer():
    def __init__(self):
        self.nodes = {}
        self.ways = {}
        self.relations = {}

    def asXML(self):
        xml = '''<?xml version='1.0' encoding='UTF-8'?>\n<osm version='0.6' upload='false' generator='Python script'>'''
        for n in self.nodes:
            xml += self.nodes[n].asXML()
        for w in self.ways:
            xml += self.ways[w].asXML()
        for r in self.relations:
            xml += self.relations[r].asXML()

        xml += '''</osm>'''
        return xml

class OSM_Primitive():
    counter = -10000

    def __init__(self, ml, primitive, attributes = {}, tags={}):
        self.attributes = attributes
        self.tags = tags
        self.primitive = primitive
        print('attr: ', attributes, self.attributes)
        if not(self.attributes) or not('id' in self.attributes):
            print(OSM_Primitive.counter)
            self.attributes['action'] = 'modify'
            self.attributes['visible'] = 'true'
            self.attributes['id'] = str(OSM_Primitive.counter)
            OSM_Primitive.counter -= 1
    
    def addTags(self, tags):
        for key in tags:
            self.addTag(key, tags[key])

    def addTag(self, key, value):
        self.tags[key] = value

    def asXML(self, body=''):
        self.xml = '<{} '.format(self.primitive)
        for attr in ['id', 'lat', 'lon', 'action', 'timestamp', 'uid', 'user', 'visible', 'version', 'changeset']:
            if attr in self.attributes:
                self.xml += "{}='{}' ".format(attr, self.attributes[attr])
        self.xml += '>'
        if body: self.xml += body
        for key in self.tags:
            self.xml += "\n  <tag k='{key}' v='{tag}' />".format(key=key, tag=self.tags[key])
        self.xml += '\n</{}>'.format(self.primitive)
        return self.xml

#    def __repr__(self):
#        return self.asXML()        
class Node(OSM_Primitive):
    def __init__(self, ml, attributes={}, tags={}):
        if not(attributes):
            attributes={'lon': '0.0', 'lat': '0.0'}

        super().__init__(ml, primitive='node', attributes = attributes, tags=tags)
        ml.nodes[self.attributes['id']] = self

class Way(OSM_Primitive):
    def __init__(self, ml, attributes={}, nodes=[], tags={}):
        '''Ways are built up as an ordered sequence of nodes
           it can happen we only know the id of the node,
           or we might have a Node object with all the details'''
        super().__init__(ml, primitive='way', attributes = attributes, tags=tags)
        self.nodes = []
        self.addNodes(nodes)
        ml.ways[self.attributes['id']] = self

    def addNodes(self,nodes):
        for n in nodes:
            self.addNode(n)

    def addNode(self,node):
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

class RelationMember():
    def __init__(self, role='', primtype='', member=None):
        self.primtype = primtype
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
    def __init__(self, ml, members=[], tags={}, attributes = {}):
        super().__init__(ml, primitive='relation', attributes = attributes, tags=tags)

        self.members = []
        self.addMembers(members)
        ml.relations[self.attributes['id']] = self
        print (ml.relations)
    def addMembers(self,members):
        for m in members:
            self.addMember(m)

    def addMember(self,member):
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

    def __init__(self, ml, lon=0.0, lat=0.0, tags={}):
        super().__init__(ml, lon, lat, tags)
        self.tags['highway'] = 'bus_stop'
        self.tags['public_transport'] = 'platform'

class PT_StopArea(Relation):
    pass

class PT_Route(Relation):
    '''This is what we think of as a variation of a line'''
    def __init__(self, ml, members=[], tags={}, attributes = {}):
        tags['type'] = 'route'
        print('attr PT: ', attributes)
        super().__init__(ml, attributes = attributes, tags=tags)

class PT_RouteMaster(Relation):
    '''This is what we think of as a publick transport line
       It contains route relations for each variation of an itinerary'''
    def __init__(self, ml, members=[], tags={}, attributes = {}):
        tags['type'] = 'route_master'
        super().__init__(ml, attributes = attributes, tags=tags)

    def addRoute(self, route):
        m = RelationMember(primtype = 'relation', role = '', member = route)
        super().addMember(m)

