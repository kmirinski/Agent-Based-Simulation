from dataclasses import asdict
import tornado
import asyncio
import json
import random
from network import build_network
from environment import build_environment
from data_logger import *
import pandas as pd
import numpy as np

# ---------------------------------------------------------

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
            "links": links_data
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
        vehicles = [asdict(vehicle) for vehicle in network.node_vehicles[node_id]]
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

        vehicles = [asdict(vehicle) for vehicle in network.link_vehicles[link_id]]

        self.write(json.dumps(vehicles))

class SnapshotHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        # Enable CORS by setting appropriate headers
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def get(self): 
        # randomize_snapshot()
        get_snapshot()
        
        link_intensites =  [ sum([vehicle.quantity for vehicle in vehicles]) for vehicles in network.link_vehicles] 
        response = {
            "link_intensities": link_intensites
        }
        self.write(json.dumps(response))

# ---------------------------------------------------------

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

# ---------------------------------------------------------

def read_data_network():
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

    return nodes_df, connectivity_df

def read_data_environment():
    requests_df = pd.read_csv('Server/instance_files_test/param_demand_test.csv')
    nodes_df = pd.read_csv('Server/instance_files_test/param_nodes_test.csv')
    vehicles_df = pd.read_csv('Server/instance_files_test/param_vehicles_test.csv')

    with open('Server/instance_files_test/param_dist_test.csv') as f:
        f.readline().strip().split(',')
        dist_matrix = pd.read_csv(f, header=None).values

    print("Data read successfully")

    return requests_df, nodes_df, dist_matrix, vehicles_df

def read_data_services():
    services_df = pd.read_csv('Server/instance_files_test/param_services_test.csv')
    return services_df

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

def get_snapshot():
    vehicle_matrix = environment.step()
    if vehicle_matrix is not None:
        network.update_vehicles(vehicle_matrix)
        return True
    else:
        return False

# ---------------------------------------------------------

def initialize():
    """
    Initialize the simulation by reading the data and creating the network and environment objects.
    """
    nodes_df_network, connectivity_df = read_data_network()
    requests_df, nodes_df_env, dist_matrix, vehicles_df = read_data_environment()
    services_df = read_data_services()
    # print(services_df)
    # print("#########################")
    # print(requests_df)
    step_size = 1

    network = build_network(nodes_df_network, connectivity_df)
    environment = build_environment(requests_df, nodes_df_env, dist_matrix, vehicles_df, services_df, step_size)

    create_folder_and_file(FOLDER_NAME, EVENT_FILE, EVENTS_FILE_PATH)
    create_folder_and_file(FOLDER_NAME, ENVIRONMENT_STATES_FILE, ENVIRONMENT_STATES_FILE_PATH)
    create_folder_and_file(FOLDER_NAME, VEHICLE_STATES_FILE, VEHICLE_STATES_FILE_PATH)
    create_folder_and_file(FOLDER_NAME, CALCULATIONS_FILE, CALCULATIONS_FILE_PATH)

    return network, environment

def run_simulation():
    # asyncio.run(main()) # for debug
    while get_snapshot():
        pass
    print("Simulation completed")
    
def save_results():
    # Save events
    environment.event_logger.log_events()
    # Save environment states
    environment.state_logger.log_states()
    # Save overall calculations
    environment.statistics_tracker.log_statistics()
    print("Results saved successfully")

def send_results():
    pass

# ---------------------------------------------------------

if __name__ == "__main__":

    network, environment = initialize()
    run_simulation()
    save_results()
    send_results()
    