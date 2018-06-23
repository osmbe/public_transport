from dblogin import db

import django
from django.conf import settings
settings.configure()

django.setup()

#from lines.models import Line

import calculateRouteRelationsForLine

allrouteidentifiersDeLijn = db.prepare("""SELECT 
                                              rte.routeidentifier,
                                              rte.routepublicidentifier AS routepublicidentifier
                                          FROM 
                                            DL_routes rte
                                          WHERE
                                               rte.routepublicidentifier !~* 'F'
                                           AND rte.routedescription !~* 'Feestbus'
                                          ORDER BY
                                            rte.routeidentifier;""")

for line in allrouteidentifiersDeLijn():
    print ('line: ', line)
    l = line[0]
    print (l)
    xml = calculateRouteRelationsForLine.JOSM_RC("De Lijn", l)

    print (xml)

    

