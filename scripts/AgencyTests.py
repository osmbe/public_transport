import unittest, os, overpy
from scripts.Agency import Agency

class AgencyTestCase(unittest.TestCase):
    with open(os.path.join(os.path.split(os.getcwd())[0],
                           'test_data','DeLijn1305.osm')) as fh:
        xml_data = fh.read()

    def test_reproducability(self):
        delijn = Agency(name='De Lijn',
                        zone_tag='zone:De_Lijn',
                        ref_tag='ref:De_Lijn',
                        route_ref_tag='route_ref:De_Lijn')

        api = overpy.Overpass()
        delijn.data = api.parse_xml(data=self.xml_data,
                                    encoding='utf-8',
                                    parser=None)


        #self.assertEqual(delijn.map_layer.xml(), self.xml_data)


if __name__ == '__main__':
    unittest.main()
