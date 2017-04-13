# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.contrib.gis.db import models

class Calendar(models.Model):
    vscid = models.IntegerField(primary_key=True)
    vsid = models.BigIntegerField(blank=True, null=True)
    vscdate = models.DateField(blank=True, null=True)
    vscday = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'calendar'

class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'

class Places(models.Model):
    placeid = models.IntegerField(primary_key=True)
    placeidentifier = models.TextField(blank=True, null=True)
    placedescription = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'places'

class Routes(models.Model):
    routeid = models.IntegerField(primary_key=True)
    routeidentifier = models.TextField(blank=True, null=True)
    routedescription = models.TextField(blank=True, null=True)
    routepublicidentifier = models.TextField(blank=True, null=True)
    routeversion = models.TextField(blank=True, null=True)
    routeservicetype = models.TextField(blank=True, null=True)
    routeservicemode = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'routes'

class Segments(models.Model):
    segmentid = models.BigIntegerField(primary_key=True)
    tripid = models.ForeignKey('Trips', models.DO_NOTHING, db_column='tripid', blank=True, null=True)
    stopid = models.ForeignKey('Stops', models.DO_NOTHING, db_column='stopid', blank=True, null=True)
    segmentsequence = models.IntegerField(blank=True, null=True)
    segmentstart = models.TextField(blank=True, null=True)
    segmentend = models.TextField(blank=True, null=True)
    segmentshiftstart = models.IntegerField(blank=True, null=True)
    segmentshiftend = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'segments'

class SpatialRefSys(models.Model):
    srid = models.IntegerField(primary_key=True)
    auth_name = models.CharField(max_length=256, blank=True, null=True)
    auth_srid = models.IntegerField(blank=True, null=True)
    srtext = models.CharField(max_length=2048, blank=True, null=True)
    proj4text = models.CharField(max_length=2048, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'spatial_ref_sys'

class Stops(models.Model):
    stopid = models.IntegerField(primary_key=True)
    stopidentifier = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    street = models.TextField(blank=True, null=True)
    municipality = models.TextField(blank=True, null=True)
    parentmunicipality = models.TextField(blank=True, null=True)
    x = models.IntegerField(blank=True, null=True)
    y = models.IntegerField(blank=True, null=True)
    stopisaccessible = models.NullBooleanField()
    stopispublic = models.NullBooleanField()
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    route_ref = models.TextField(blank=True, null=True)
    osm_name = models.TextField(blank=True, null=True)
    osm_city = models.TextField(blank=True, null=True)
    osm_street = models.TextField(blank=True, null=True)
    osm_operator = models.TextField(blank=True, null=True)
    osm_route_ref = models.TextField(blank=True, null=True)
    osm_source = models.TextField(blank=True, null=True)
    osm_node_id = models.TextField(blank=True, null=True)
    osm_last_modified_by_user = models.TextField(blank=True, null=True)
    osm_last_modified_timestamp = models.DateTimeField(blank=True, null=True)
    osm_zone = models.TextField(blank=True, null=True)
    zoneid = models.IntegerField(blank=True, null=True)
    # Geo Django field to store a point
    geomdl = models.PointField(help_text="Represented as (longitude, latitude)")
    geomosm = models.PointField(help_text="Represented as (longitude, latitude)")

    # You MUST use GeoManager to make Geo Queries
    objects = models.GeoManager()
    #geomdl = models.TextField(blank=True, null=True)  # This field type is a guess.
    #geomosm = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'stops'

class StopsDl(models.Model):
    stopspk = models.IntegerField(primary_key=True)
    last_change_timestamp = models.DateTimeField(blank=True, null=True)
    stopidentifier = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    street = models.TextField(blank=True, null=True)
    municipality = models.TextField(blank=True, null=True)
    parentmunicipality = models.TextField(blank=True, null=True)
    stopisaccessible = models.NullBooleanField()
    stopispublic = models.NullBooleanField()
    route_ref = models.TextField(blank=True, null=True)
    geomdl = models.PointField(help_text="Represented as (longitude, latitude)")

    class Meta:
        managed = False
        db_table = 'stops_dl'

class StopsOsm(models.Model):
    stopspk = models.IntegerField(primary_key=True)
    last_change_timestamp = models.DateTimeField(blank=True, null=True)
    ref = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    operator = models.TextField(blank=True, null=True)
    route_ref = models.TextField(blank=True, null=True)
    zone = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    node_id = models.TextField(blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    last_modified_by = models.TextField(blank=True, null=True)
    geomosm = models.PointField(help_text="Represented as (longitude, latitude)")

    class Meta:
        managed = False
        db_table = 'stops_osm'

class Trips(models.Model):
    tripid = models.BigIntegerField(primary_key=True)
    routeid = models.ForeignKey(Routes, models.DO_NOTHING, db_column='routeid', blank=True, null=True)
    vscid = models.ForeignKey(Calendar, models.DO_NOTHING, db_column='vscid', blank=True, null=True)
    tripnoteidentifier = models.TextField(blank=True, null=True)
    tripnotetext = models.TextField(blank=True, null=True)
    tripstart = models.TextField(blank=True, null=True)
    tripend = models.TextField(blank=True, null=True)
    tripshiftstart = models.IntegerField(blank=True, null=True)
    tripshiftend = models.IntegerField(blank=True, null=True)
    tripnoteidentifier2 = models.TextField(blank=True, null=True)
    tripnotetext2 = models.TextField(blank=True, null=True)
    placeidstart = models.ForeignKey(Places, models.DO_NOTHING, db_column='placeidstart', blank=True, null=True, related_name='placeidstartFK')
    placeidend = models.ForeignKey(Places, models.DO_NOTHING, db_column='placeidend', blank=True, null=True, related_name='placeidendFK')
    naturalkey = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trips'
