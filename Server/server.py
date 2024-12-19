from dataclasses import asdict
import tornado
import asyncio
import json
import random
from network import build_network, Vehicle
import pandas as pd
import numpy as np


class SetupHandler(tornado.web.RequestHandler):
    """
    Endpoint that handles setting up the simulation. Provides information such as the nodes and links in the network
    """
    def set_default_headers(self):
        # Enable CORS by setting appropriate headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    
    def get(self):
        # Prepare the data to send (only nodes and links)
        nodes_data = [asdict(node) for node in network.nodes]  # Convert nodes to dict
        links_data = [asdict(link) for link in network.links]  # Convert links to dict
        
        
        # Combine into a response
        response = {
            "nodes": nodes_data,
            "links": links_data,
            'vehicle_types': ['Empty Truck', 'Container'] # todo: figure out where and how to declare the kinds of vehicles involved in the simulation
        }

        # Send the response as JSON
        self.write(json.dumps(response))


class NodeHandler(tornado.web.RequestHandler):
    """
    Request handler that returns the information for a specific node based on node_id passed as a query parameter.
    """
    def set_default_headers(self):
        # Enable CORS by setting appropriate headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def get(self):
        # Get the node_id from the query parameters, using a default if it's not provided
        node_id = int(self.get_argument("node_id", None))
        visible_vehicles = json.loads(self.get_argument("visible_vehicles"))
        vehicles = [asdict(vehicle) for vehicle in network.node_vehicles[node_id] if vehicle.name in visible_vehicles]
        self.write(json.dumps(vehicles))

class LinkHandler(tornado.web.RequestHandler):
    """
    Request handler that returns the information for a specific node based on node_id passed as a query parameter.
    """
    def set_default_headers(self):
        # Enable CORS by setting appropriate headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def get(self):
        # Get the node_id from the query parameters, using a default if it's not provided
        link_id = int(self.get_argument("link_id", None))
        visible_vehicles = json.loads(self.get_argument("visible_vehicles"))
        vehicles = [asdict(vehicle) for vehicle in network.link_vehicles[link_id] if vehicle.name in visible_vehicles]

        self.write(json.dumps(vehicles))
    

class SnapshotHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # Enable CORS by setting appropriate headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def get(self): 
        updateSimulation = json.loads(self.get_argument('next_snapshot'))
        if updateSimulation:
            randomize_snapshot()
        visible_vehicles = json.loads(self.get_argument("visible_vehicles"))

        link_intensites =  [ sum([vehicle.quantity for vehicle in vehicles if vehicle.name in visible_vehicles]) for vehicles in network.link_vehicles] 
        response = {
            "link_intensities": link_intensites
        }
        self.write(json.dumps(response))


def make_app():
    return tornado.web.Application([
        (r"/setup", SetupHandler),
        (r"/snapshot", SnapshotHandler),
        (r"/node", NodeHandler),
        (r"/link", LinkHandler),
    ])

async def main():
    app = make_app()
    app.listen(8888)
    await asyncio.Event().wait()




if __name__ == "__main__":
    city_names = ["Amsterdam", "Brussel", "Antwerp"]
    city_coordinates = [
        [4.9041, 52.3676],
        [4.3572, 50.8477],
        [4.4150, 51.2199]
    ]

    # test nodes DataFrame
    nodes_df = pd.DataFrame({
        'long_name': city_names,
        'longitude': [coords[0] for coords in city_coordinates],
        'latitude': [coords[1] for coords in city_coordinates]
    })

    # test connectivity DataFrame
    connectivity_data = [
        (0, 1),  # Amsterdam to Brussel
        (0, 2),  # Amsterdam to Antwerp
        (1, 2),  # Brussel to Antwerp
        (2, 1)   # Antwerp to Brussel
    ]
    connectivity_df = pd.DataFrame(connectivity_data, columns=['origin', 'destination'])
    connectivity_df['origin'] = connectivity_df['origin']
    connectivity_df['destination'] = connectivity_df['destination']

    network = build_network(nodes_df, connectivity_df)


    def randomize_snapshot():
        """
        for testing only, randomizes resources in network
        """

        empty_trucks = np.array([
            [random.randint(1,100), random.randint(1,100), random.randint(1,100)],
            [0, random.randint(1,100), random.randint(1,100)],
            [0, random.randint(1,100), random.randint(1,100)]
        ]) # same nonzero entries as connectivity matrix, except with diagonals
        containers = np.array([
            [random.randint(1,100), random.randint(1,100), random.randint(1,100)],
            [0, random.randint(1,100), random.randint(1,100)],
            [0, random.randint(1,100), random.randint(1,100)]
        ]) 
        
        network.update_vehicles({"Empty Truck": empty_trucks, "Container": containers})
    

    asyncio.run(main())