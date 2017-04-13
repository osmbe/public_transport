from django.contrib.gis import admin
from . import models

class StopsAdmin(admin.GeoModelAdmin):

    search_fields = ['name','uuid']
    #list_display = ['uuid','name','point',]
    #readonly_fields = ['uuid','slug',]

admin.site.register(models.Stops, StopsAdmin)

