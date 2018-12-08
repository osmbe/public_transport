from unittest import TestCase
import OSM_data_model as osm

class TestPublicTransportRouteMaster(TestCase):
    def test_add_route(self):
        ml = osm.MapLayer()
        member1 = osm.RelationMember(ml,
                                     member = osm.PublicTransportRoute(ml),
                                     type='relation')
        member2 = osm.RelationMember(ml,
                                     member = osm.PublicTransportRoute(ml),
                                     type='relation')
        rm = osm.PublicTransportRouteMaster(ml,
                                            members=[member1, member2])
        print (rm.xml)
