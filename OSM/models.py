from django.contrib.gis.db import models
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
# from django.contrib.gis.db.models.manager import GeoManager

class KeyValueString(models.Model):
    '''All possible text strings for keys and values of tags'''
    content = models.TextField()

    def __str__(self):
        return self.content


class Tag(models.Model):
    '''All key/value combinations'''
    key = models.ForeignKey(KeyValueString, related_name='keys', on_delete=models.CASCADE)
    value = models.ForeignKey(KeyValueString, related_name='values', on_delete=models.CASCADE)

    def __str__(self):
        return '"{}"= "{}"'.format(self.key, self.value)

    def add_tag(self, key, value):
        found_key=KeyValueString.objects.get(content=key)
        if found_key:
            self.key = found_key
        else:
            self.key = KeyValueString(content=key)

        found_value = KeyValueString.objects.get(content=value)
        if found_value:
            self.value = found_value
        else:
            self.key = KeyValueString(content=value)
            self.value = Value(value=value)

        self.save()
        return self

#    def save(self, *args, **kwargs):
#
#        __super__.save(*args, **kwargs)

class OSM_Primitive(models.Model):
    id = models.BigIntegerField(primary_key=True)
    action = models.CharField(max_length=16)
    timestamp = models.DateTimeField()
    uid = models.IntegerField()
    user = models.TextField()
    visible = models.BooleanField()
    version = models.IntegerField()
    changeset = models.IntegerField()
    tags = models.ManyToManyField(Tag)
    incomplete = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def add_tag(self, save=True, key, value):
        """It is important to note that a key can only occur once per element.
           How to enforce that? it's probably OK to "overwrite" its value"""
        self.tags = Tag.add_tag(key=key, value=value)
        if save:
            self.save()
        return self

    def add_tags(self, tagsdict):
        for k, v in tagsdict:
            self.add_tag(save = False, key=k, value=v)
        self.save()
        return self


class Node(OSM_Primitive):
    geom = models.PointField(geography=True, spatial_index=True)
    #objects = models.manager.GeoManager()

    @property
    def coordinates(self):
        return str(self.geom.x), str(self.geom.y)

    @coordinates.setter
    def coordinates(self, lon, lat):
        self.geom = Point(lon, lat)
        self.save()


class WayNodes(models.Model):
    sequence = models.PositiveIntegerField()


class Way(OSM_Primitive):
    '''Ways usually have several nodes,
       nodes can belong to more than 1 way'''
    nodes = models.ManyToManyField(Node, through='WayNodes')

    def add_node(self, node):
        # get highest sequence number for this way
        # add node to WayNodes table with incremented sequence number
        # what if the node is not in the DB?
        # should WayNodes have an extra field for the node id, in case the link can't be made?
        # or should there be a 'dummy' in the nodes table so we have something to point to?
        # I created an extra attribute to indicate we don't have all the information
        # for a primitive
        wn=WayNodes(node = node,
                    way = self,
                    sequence = self.waynodes.set.max()+1)
        wn.save()
        return wn

class RelationMember(models.Model):
    NODE = 'n'
    WAY = 'w'
    RELATION = 'r'
    TYPES = (
        (NODE, 'node'),
        (WAY, 'way'),
        (RELATION, 'relation')
    )
    type = models.CharField(max_length=1, choices=TYPES)
    role = models.TextField()
    sequence = models.PositiveIntegerField()
    member_node = models.OneToOneField(Node)
    member_way = models.OneToOneField(Way)
    member_rel = models.OneToOneField('Relation', related_name='child_relations')


class Relation(OSM_Primitive):
    members = models.ForeignKey(RelationMember, on_delete=models.CASCADE)

    def add_member(self, member):
        return WayNodes(node = node,
                        way = self,
                        sequence = self.waynodes.set.max()+1)
