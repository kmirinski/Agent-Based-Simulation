import urllib.request
import json

def get_route(origin_lon, origin_lat, dest_lon, dest_lat):
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?geometries=geojson&overview=full"
    contents = urllib.request.urlopen(url).read()
    contents = json.loads(contents)
    contents = contents['routes'][0]['geometry']['coordinates']
    return contents

print(get_route(4.9041, 52.3676, 4.3572, 50.8477))