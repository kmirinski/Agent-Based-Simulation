import json
import geojson
import pandas as pd
import urllib.request

def get_route(origin_longitude, origin_latitude, dest_longitude, dest_latitude, return_distance=False):
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_longitude},{origin_latitude};{dest_longitude},{dest_latitude}?geometries=geojson&overview=full"
    contents = urllib.request.urlopen(url).read()
    contents = json.loads(contents)
    total_distance = contents['routes'][0]['legs'][0]['distance'] / 1000 # distance in km
    path = contents['routes'][0]['geometry']['coordinates']

    return path if not return_distance else (path, total_distance)

def save_route(origin_name, origin_longitude, origin_latitude, dest_name, dest_longitude, dest_latitude, out_folder='instance_files/routes/'):
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_longitude},{origin_latitude};{dest_longitude},{dest_latitude}?geometries=geojson&overview=full"
    contents = urllib.request.urlopen(url).read()
    contents = json.loads(contents)
    route = contents['routes'][0]
    with open(f"{out_folder}/{origin_name}_{dest_name}.geojson", 'w') as f:
        geojson.dump(route, f)

def cache_local_routes(out_folder='instance_files/routes/'):
    cities = pd.read_csv('./instance_files/cities.csv', header=0)
    for i in range(len(cities)):
        for j in range(len(cities)):
            if i != j:
                save_route(cities.iloc[i]['name'], cities.iloc[i]['lng'], cities.iloc[i]['lat'], cities.iloc[j]['name'], cities.iloc[j]['lng'], cities.iloc[j]['lat'], out_folder)


get_route(4.3517, 50.8503, 3.2247, 51.2093)