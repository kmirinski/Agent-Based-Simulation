from dataclasses import dataclass
from typing import Tuple, List, Dict
from router import get_route
import pandas as pd
import json


@dataclass
class Node:
    name: str
    longitude: float
    latitude: float

@dataclass
class Link:
    start_longitude: float
    start_latitude: float
    end_longitude: float
    end_latitude: float

@dataclass
class Vehicle:
    """
    A type of vehicle is defined by it's type name (e.g. empty trucks and containers), origin node (ID), destination node (ID), and quantity
    """
    name: str
    origin: int
    destination: int
    quantity: int

@dataclass
class Network:
    """
    A network is constructed as:
        - a list of nodes, where the index serves as the node ID
        - a list of links, where the index serves as the link ID
        - a dictionary from (int, int) to [int], which represents a mapping (in terms of their IDs) from source-destination node pair
          to the list of links along the path.
        - a link_id_lookup dictionary that maps (start_longitude, start_latitude, end_longitude, end_latitude) to link ID.
        - link_vehicles is a list that records the resources on each link.
        - node_vehicles is a list that records the resources at each node.
    """
    nodes: List[Node]
    links: List[Link]
    paths: Dict[Tuple[int, int], List[int]]
    link_id_lookup: Dict[Tuple[float, float, float, float], int] = None
    link_vehicles: List[Vehicle] = None
    node_vehicles: List[Vehicle] = None
    
    def __post_init__(self):
        # Compute link_id_lookup if it is not provided
        if self.link_id_lookup is None:
            self.link_id_lookup = {
                (link.start_longitude, link.start_latitude, link.end_longitude, link.end_latitude): idx
                for idx, link in enumerate(self.links)
            }
        if self.link_vehicles is None:
            self.link_vehicles = [[] for _ in self.links]
        if self.node_vehicles is None:
            self.node_vehicles = [[] for _ in self.nodes]


def build_network(nodes: pd.DataFrame, connectivity: pd.DataFrame) -> Network:
    """
    Build a network by reading from nodes and connectivity.
    Args:
        nodes (pd.DataFrame): DataFrame with columns ['long_name', 'longitude', 'latitude'].
        connectivity (pd.DataFrame): DataFrame with columns ['origin', 'destination'].
    Returns:
        Network: Constructed network with nodes, links, paths, and link_id_lookup.
    """
    # Create the list of nodes
    node_list = [
        Node(name=row['long_name'], longitude=row['longitude'], latitude=row['latitude'])
        for _, row in nodes.iterrows()
    ]
    
    unique_links = {}  # Dictionary to store unique links as key-value pairs
    links = []  # List to hold the unique Link objects
    paths = {}  # Dictionary to hold the paths

    # Iterate over the connectivity data to create paths and populate links
    for _, row in connectivity.iterrows():
        origin_id = int(row['origin']) # NB: numpy int cannot be serialized to JSON, so we need to convert to native int
        destination_id = int(row['destination'])
        
        # Get origin and destination coordinates
        origin_node = node_list[origin_id]
        dest_node = node_list[destination_id]
        
        # Fetch route using get_route
        route = get_route(
            origin_node.longitude, origin_node.latitude,
            dest_node.longitude, dest_node.latitude
        )
        
        # Map the route to link IDs
        link_ids = []
        for i in range(len(route) - 1):
            start_longitude, start_latitude = route[i]
            end_longitude, end_latitude = route[i + 1]
            
            # Ensure the link is represented in a consistent order
            link_key = (start_longitude, start_latitude, end_longitude, end_latitude)
            
            if link_key not in unique_links:
                # Create a new Link and add it to the list
                unique_links[link_key] = len(links)
                links.append(Link(
                    start_longitude=start_longitude, start_latitude=start_latitude,
                    end_longitude=end_longitude, end_latitude=end_latitude
                ))
            
            # Add the link ID to the path
            link_ids.append(unique_links[link_key])
        
        # Map the source-destination pair to the list of link IDs
        paths[(origin_id, destination_id)] = link_ids
    
    # Return the constructed network
    return Network(nodes=node_list, links=links, paths=paths, link_id_lookup=unique_links)