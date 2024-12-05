import json
import urllib.request

def get_route(origin_longitude, origin_latitude, dest_longitude, dest_latitude):
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_longitude},{origin_latitude};{dest_longitude},{dest_latitude}?geometries=geojson&overview=full"
    contents = urllib.request.urlopen(url).read()
    contents = json.loads(contents)
    contents = contents['routes'][0]['geometry']['coordinates']
    return [tuple(c) for c in contents]
