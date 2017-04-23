from __future__ import unicode_literals

from django.contrib.gis.db import models

class Stop(models.Model):
    '''This model tracks changes. Data from OSM and the various operators comes in through discardable tables. That data is then converted and stored here. If data for this stop was already present in this table, the field gets updated. If this means that something should be changed in OSM, the changed_by_operator flag gets set. I'm not sure at the moment whether it should be more specific: name changed, location changed, abolished
Changes can happen in OSM as well.
It's then up to the user to decide how to act upon these changes. If the user makes changes, they should get a link to go and apply them in JOSM.

Use cases:
stop exists in OSM
change comes in through one of the operators
fields are compared and updated if needed, changed_by_operator flag gets set
user gets change to make changes using JOSM_RC, with updated data

stop exists in OSM
some tags are modified or it is moved
fields are compared, change is detected and changed_in_osm flag gets set
user gets change to make changes using JOSM_RC, with updated data

stop is removed from OSM
we detect this based on OSM id, now we need to look if the operator still has it
give user possibility to revert deletion or to remove our record

stop is removed from operator's DB
check if this was the only operator for that stop, give user possibility to delete it using JOSM
JOSM RC probably should only do zoom_and_download
if the stop is served by more than 1 operator, change the tags accordingly.

stop is added in operator's DB
no stop with corresponding ref is found in OSM, this should be a separate view to list these

There should also be a view where one can see that the distance between OSM and where the operator thinks their stop is,is more than 5 meters

There should be a possibility to mark certain differences as OK
* sometimes the names coming from the operator aren't what we want to use in OSM
* sometimes the positions are off

ref and route_ref should always be updated in OSM, operator should be authoritative on those

'''
    osm_id = models.TextField(primary_key=True, help_text="composed of n, w, r + id in OSM")
    changed_in_osm = models.BooleanField()
    changed_by_operator = models.BooleanField()
    timestamp = models.DateTimeField(blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    name_de_lijn = models.TextField(blank=True, null=True)
    name_tec = models.TextField(blank=True, null=True)
    name_nl = models.TextField(blank=True, null=True)
    name_fr = models.TextField(blank=True, null=True)
    name_en = models.TextField(blank=True, null=True)
    name_de = models.TextField(blank=True, null=True)
    ref = models.TextField(blank=True, null=True)
    ref_de_lijn = models.TextField(blank=True, null=True)
    ref_tecb = models.TextField(blank=True, null=True)
    ref_tecc = models.TextField(blank=True, null=True)
    ref_tech = models.TextField(blank=True, null=True)
    ref_tecn = models.TextField(blank=True, null=True)
    ref_tecl = models.TextField(blank=True, null=True)
    ref_tecx = models.TextField(blank=True, null=True)
    route_ref = models.TextField(blank=True, null=True)
    route_ref_de_lijn = models.TextField(blank=True, null=True)
    route_ref_tecb = models.TextField(blank=True, null=True)
    route_ref_tecc = models.TextField(blank=True, null=True)
    route_ref_tech = models.TextField(blank=True, null=True)
    route_ref_tecn = models.TextField(blank=True, null=True)
    route_ref_tecl = models.TextField(blank=True, null=True)
    route_ref_tecx = models.TextField(blank=True, null=True)
    zone = models.TextField(blank=True, null=True)
    zone_de_lijn = models.TextField(blank=True, null=True)
    zone_tec = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    dummy = models.TextField(blank=True, null=True)
    operator =  models.ForeignKey("operators.Operator", on_delete=models.CASCADE)

    # Geo Django field to store a point
    #geom = models.PointField(help_text="Represented as (longitude, latitude)")
    # You MUST use GeoManager to make Geo Queries
    #objects = models.GeoManager()
    
    def __str__(self):
        return '{} {} {} {}'.format(self.name, self.operator, self.ref, )

class StopFromOperator(models.Model):
    osmid = models.ForeignKey(Stop, null=True, blank=True, default = None)
    operator =  models.ForeignKey("operators.Operator", on_delete=models.CASCADE)
    offset = models.FloatField(blank=True, null=True)
    identifier = models.TextField(blank=True, null=True)
    route_ref = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    street = models.TextField(blank=True, null=True)
    stopisaccessible = models.NullBooleanField()
    
    #geom = models.PointField(help_text="Represented as (longitude, latitude)")
    #objects = models.GeoManager()

