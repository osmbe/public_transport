from sys import stdout
from requests import post

fn = 'data/OSM/stops.csv'
query=r'''[timeout:300][out:csv(::id, ::lat, ::lon, ::type, ::timestamp, ::version, ::user,"name", "name:De_Lijn",
                                "name:TEC", "name:nl", "name:fr", "name:en", "name:de", "ref", "ref:De_Lijn",
                                "ref:TECB", "ref:TECC", "ref:TECH", "ref:TECN", "ref:TECL", "ref:TECX", "route_ref",
                                "route_ref:De_Lijn", "route_ref:TECB", "route_ref:TECC", "route_ref:TECH",
                                "route_ref:TECN", "route_ref:TECL", "route_ref:TECX", "zone", "zone:De_Lijn",
                                "zone:TEC", "source", "operator";false;'\t')];

(
    node
      ["highway"="bus_stop"]
      ["operator"~"De Lijn"];
    node
      ["railway"="tram_stop"]
      ["operator"~"De Lijn"];
    node
      ["public_transport"="platform"]
      ["operator"~"De Lijn"];
  ) -> .stopsPlatformsAndStopPositions;            // All bus_stop, tram_stop, platform nodes 
                                                   // inside of Belgium and some outside of Belgium
                                                   // in case they are served by De Lijn or TEC

out meta;'''

print('Performing Overpass query, please be patient')
print('============================================')
print()
stdout.flush()

response = post("http://overpass-api.de/api/interpreter", query)

print(response)

with open(fn, 'wb') as fh:
    fh.write(response.content)

print('Data downloaded')


