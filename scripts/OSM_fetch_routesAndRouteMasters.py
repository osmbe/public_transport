import sys, requests
fn = 'data/OSM/routesDeLijn.osm'
query=r'''[timeout:300];

(
    relation
      ["type"="route"]
      ["operator"~"De Lijn"];
    node
      ["type"="route_master"]
      ["operator"~"De Lijn"];
  ) -> .routeAndRouteMasters;                      // All route and route_master relations 
                                                   // inside of Belgium and some outside of Belgium
                                                   // in case they are served by De Lijn 

out meta;'''

print('Performing Overpass query, please be patient')
print('============================================')
print()
sys.stdout.flush()

response = requests.post("http://overpass-api.de/api/interpreter", query)

print(response)

with open(fn, 'wb') as fh:
    fh.write(response.content)

print('Data downloaded')


