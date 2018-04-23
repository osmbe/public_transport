from django.db import models

#!/bin/python

class OSM_Primitive():
    osm_id = str(OSM_Primitive.counter)
    action = 'modify'
    visible = 'true'
    timestamp
    uid
    user
    visible
    version
    changeset

class Tag(models.Model):
    tag = models.CharField(max_length=100)
class Value(models.Model):
    value = models.CharField(max_length=512)

class Node(OSM_Primitive):
    def __init__(self, ml, attributes = None, tags = None):
        if not(attributes):
            attributes={'lon': '0.0', 'lat': '0.0'}

        super().__init__(ml, primitive='node', attributes = attributes, tags=tags)
        ml.nodes[self.attributes['id']] = self

class Way(OSM_Primitive):
    def __init__(self, ml, attributes = None, nodes = None, tags = None):
        '''Ways are built up as an ordered sequence of nodes
           it can happen we only know the id of the node,
           or we might have a Node object with all the details'''
        super().__init__(ml, primitive='way', attributes = attributes, tags=tags)
        self.nodes = []
        self.addNodes(nodes)
        ml.ways[self.attributes['id']] = self

    def addNodes(self,nodes):
        if nodes:        
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
    def __init__(self, role='', primtype='', member = None):
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
    def __init__(self, ml, members = None, tags = None, attributes = None):
        super().__init__(ml, primitive='relation', attributes = attributes, tags=tags)

        self.members = []
        self.addMembers(members)
        ml.relations[self.attributes['id']] = self
        print (ml.relations)
    def addMembers(self,members):
        if members:
            for m in members:
                self.addMember(m)

    def addMember(self,member):
        self.members.append(member)

    def asXML(self):
        body = ''
        for member in self.members:
            body += member.asXML

        return super().asXML(body=body)

class PT_Stop(Node):
    '''In this model a public transport stop is always mapped on a node with public_transport=platform tag
       This is a simplification, which makes sure there are always coordinates. In most cases this node
       represents the pole to which the flag with all details for the stop is mounted'''

    def __init__(self, ml, lon=0.0, lat=0.0, tags = None):
        super().__init__(ml, lon, lat, tags)
        self.tags['highway'] = 'bus_stop'
        self.tags['public_transport'] = 'platform'

class PT_StopArea(Relation):
    pass

class PT_Route(Relation):
    '''This is what we think of as a variation of a line'''
    def __init__(self, ml, members = None, tags = None, attributes = None):
        tags['type'] = 'route'
        print('attr PT: ', attributes)
        super().__init__(ml, attributes = attributes, tags = tags)

class PT_RouteMaster(Relation):
    '''This is what we think of as a publick transport line
       It contains route relations for each variation of an itinerary'''
    def __init__(self, ml, members = None, tags = None, attributes = None):
        tags['type'] = 'route_master'
        super().__init__(ml, attributes = attributes, tags = tags)

    def addRoute(self, route):
        m = RelationMember(primtype = 'relation', role = '', member = route)
        super().addMember(m)
