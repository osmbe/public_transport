from math import asin, cos, sin, atan2, radians, degrees, pi

from javax.swing import JOptionPane
from org.openstreetmap.josm.gui import MainApplication

import org.openstreetmap.josm.command as Command

def displace2(coor, bearing, distance):
    _bearing = radians(float(bearing))
    _lat = radians(coor.lat())
    _lon = radians(coor.lon())
    earthRadiusInMetres = 6371000.0
    dist_over_ER =  float(distance) / earthRadiusInMetres
    cos_dist_over_ER = cos(dist_over_ER)
    sin_dist_over_ER = sin(dist_over_ER)
    lat2 = asin(sin(_lat) * cos_dist_over_ER + cos(_lat) * sin_dist_over_ER * cos(_bearing))
    a = atan2(sin(_bearing) * sin_dist_over_ER * cos(_lat), cos_dist_over_ER - sin(_lat) * sin(lat2))
    lon2 = (_lon + a + 3*pi) % (2*pi) - pi
    return degrees(lon2), degrees(lat2)

def displace3(coor, bearing, distance):
    _bearing = radians(float(bearing))
    _lat = radians(coor.lat())
    _lon = radians(coor.lon())
    cos_dist_over_ER = cos(dist_over_ER)
    sin_dist_over_ER = sin(dist_over_ER)
    lat2 = asin(sin(_lat) * cos_dist_over_ER + cos(_lat) * sin_dist_over_ER * cos(_bearing))
    a = atan2(sin(_bearing) * sin_dist_over_ER * cos(_lat), cos_dist_over_ER - sin(_lat) * sin(lat2))
    lon2 = (_lon + a + 3*pi) % (2*pi) - pi
    return degrees(lon2), degrees(lat2)

def displace(coor, bearing, distance):
    earth_radius = 6371000.0  # earth's radius in meter
    print bearing, distance
    _bearing = radians(bearing)
    print _bearing, cos(_bearing), sin(_bearing)
    lat1 = radians(coor.lat())
    lon1 = radians(coor.lon())
    distoverER = float(distance) / earth_radius
    cosdistoverER = cos(distoverER)
    sindistoverER = sin(distoverER)
    print distoverER, cosdistoverER, sindistoverER
    print sin(lat1) * cosdistoverER
    print cos(lat1) * sindistoverER * cos(_bearing)
    print sin(_bearing) * sindistoverER * cos(lat1)

    lat2 = asin(sin(lat1) * cosdistoverER +
                cos(lat1) * sindistoverER * cos(_bearing))

    print cosdistoverER - sin(lat1) * sin(lat2)
    print asin(sin(lat1) * cosdistoverER +
               cos(lat1) * sindistoverER * cos(_bearing))
    print atan2(sin(_bearing) * sindistoverER * cos(lat1),
                        cosdistoverER - sin(lat1) * sin(lat2))
    print lon1 + atan2(sin(_bearing) * sindistoverER * cos(lat1),
                        cosdistoverER - sin(lat1) * sin(lat2))

    lon2 = lon1 + atan2(sin(_bearing) * sindistoverER * cos(lat1),
                        cosdistoverER - sin(lat1) * sin(lat2))

    return degrees(lon2), degrees(lat2)

editLayer = MainApplication.getLayerManager().getEditLayer()
print '==== Fresh run ===='
if editLayer and editLayer.data:
    selected_nodes = editLayer.data.getSelectedNodes()
    print selected_nodes

    if not(selected_nodes):
        JOptionPane.showMessageDialog(MainApplication.parent, "Please select node(s) to displace")
    else:
        for node in selected_nodes:
            b = int(node.get("zone:De_Lijn")) + 90
            if b > 360: b = b - 360
            print b
            lon, lat = displace2(coor = node.getCoor(),
                                 bearing=b,
                                 distance = 100.0)
            print node.getCoor().lon(), node.getCoor().lat()
            print lon, lat
            commandsList = []
            commandsList.append(Command.MoveCommand(node, lon, lat))
            MainApplication.undoRedo.add(Command.SequenceCommand(
                        "Move node", commandsList))


