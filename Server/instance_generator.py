import pandas as pd
import numpy as np
import geojson
from router import get_route
from network import Network, build_network
from environment import Environment, build_environment
from typing import Tuple

def generate_random_instance(num_nodes, num_requests, Tmax, local_routes = True) -> Tuple[Environment, Network]:
    cities = pd.read_csv('./instance_files/cities.csv', header=0)
    random_cities = cities.sample(n=num_nodes).reset_index(drop=True)

    nodes_df_network = pd.DataFrame({
        'long_name': random_cities['name'],
        'longitude': random_cities['lng'],
        'latitude': random_cities['lat']
    })

    connectivity = create_connectivity(num_nodes)

    routes = {}
    distances = np.zeros((num_nodes, num_nodes))
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i != j:
                if local_routes:
                    with open(f"instance_files/routes/{random_cities.iloc[i]['name']}_{random_cities.iloc[j]['name']}.geojson") as f:
                        local = geojson.load(f)
                        distance = local['legs'][0]['distance'] / 1000 
                        route = local['geometry']['coordinates']
                else:
                    route, distance = get_route(
                        nodes_df_network.iloc[i]['longitude'], nodes_df_network.iloc[i]['latitude'],
                        nodes_df_network.iloc[j]['longitude'], nodes_df_network.iloc[j]['latitude'],
                        return_distance=True
                    )
                routes[(i, j)] = route
                distances[i, j] = distance
    



    nodes_df_env = pd.DataFrame({
        'id': range(num_nodes),
        'type': 1,
        'name':  ['N' + str(i) for i in range(num_nodes)],
        'long_name': random_cities['name']
    })

    requests = []
    for i in range(num_requests):
        origin, dest = np.random.randint(0, num_nodes, size=2)
        amount = np.random.randint(1, 100)
        price = np.random.randint(1, 10000)
        bounds = np.random.randint(1, Tmax, size=2)
        lw = min(bounds)
        uw = max(bounds)
        selected = 1
        requests.append([i, origin, dest, amount, price, lw, uw, selected])

    requests_df = pd.DataFrame(requests, columns=['id', 'orig', 'dest', 'amount', 'price', 'lw', 'uw', 'selected'])

    return build_environment(requests_df, nodes_df_env, distances), build_network(nodes_df_network, connectivity, routes)


def create_connectivity(N):
    # Create all possible pairs using numpy broadcasting
    origin, destination = np.meshgrid(np.arange(N), np.arange(N), indexing='ij')
    
    # Flatten and filter out (i, i) pairs
    mask = origin != destination
    data = np.column_stack((origin[mask], destination[mask]))
    
    # Create DataFrame
    return pd.DataFrame(data, columns=["origin", "destination"])
