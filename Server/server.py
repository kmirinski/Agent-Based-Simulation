import tornado
import asyncio
import json
import urllib.request
import numpy as np

def get_route(origin_lon, origin_lat, dest_lon, dest_lat):
    url = f"http://router.project-osrm.org/route/v1/driving/{origin_lon},{origin_lat};{dest_lon},{dest_lat}?geometries=geojson&overview=full"
    contents = urllib.request.urlopen(url).read()
    contents = json.loads(contents)
    contents = contents['routes'][0]['geometry']['coordinates']
    return contents

class SetupHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # Enable CORS by setting appropriate headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")


    def get(self):
        city_names = ["Amstnerdam", "Brussel", "Antwerp"]
        city_coordinates = [
            [4.9041, 52.3676],
            [4.3572, 50.8477],
            [4.4150, 51.2199]
        ]
        connectivity = [
            [0,1,1],
            [1,0,1],
            [1,1,0]
        ]
        paths = [[ [] for i in range(len(connectivity))] for j in range(len(connectivity))]
        for i in range(len(city_names)):
            for j in range(len(city_names)):
                if connectivity[i][j] != 0:
                    paths[i][j] = get_route(city_coordinates[i][0], city_coordinates[i][1], 
                                            city_coordinates[j][0], city_coordinates[j][1])
        
        # router uses (lon, lat), but on the client side leaflet js uses lat lon
        for c in city_coordinates:
            c.reverse()
        for row in paths:
            for path in row:
                for edge in path:
                    edge.reverse()
        setup = {"names": city_names, "coordinates":city_coordinates, "connectivity":connectivity, "paths": paths}
        self.write(json.dumps(setup))

class SnapshotHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # Enable CORS by setting appropriate headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def get(self): 
        empty_trucks = [
            [1,2,3],
            [4,5,6],
            [7,8,9]
            ]
        containers = [
            [0, 10, 11],
            [12, 0, 13],
            [14, 15, 0]
            ]
        resources = {"Empty Trucks": empty_trucks, "Containers": containers}
        self.write(json.dumps(resources))

def make_app():
    return tornado.web.Application([
        (r"/setup", SetupHandler),
        (r"/snapshot", SnapshotHandler),
    ])

async def main():
    app = make_app()
    app.listen(8888)
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())