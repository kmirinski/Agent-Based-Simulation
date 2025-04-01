import queue
import numpy as np
import pandas as pd

from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Dict

from agents import Shipper, LSP, Carrier
from data_logger import EventLogger 

from common import Request, Event, Event_Type, Agent_Type
from vehicles import Truck, Train, Barge, Vehicle

# ---------------------------------------------------------


num_shippers = 1
num_lsps = 2
num_carriers = 4

# ---------------------------------------------------------

class EventQueue(queue.PriorityQueue):
    def peek(self):
        if self.empty():
            return None
        return self.queue[0]
    
    def print_all_events(self):
        print("Events in the queue:")
        for event in self.queue:
            print(event)

# ---------------------------------------------------------

@dataclass
class Environment:
    """
    An environment is constructed by:
        - a counter that keeps track of the current time
        - a list of the requests in the environment
        - a dictionary of agents in the environment (key: type of the agent, value: list of the agents of this type)
        - a dictionary mapping from vehicle type/name to a 2D numpy array storing the number of vehicles of that type,
                where entry (i,j) is the number of vehicles of that type going from node index i to index j. 
                Entry (i,i) is the number of vehicles of that type sitting at node index i. 
        - a priority queue that stores the events happening in the environment - the priority is the timestamp of the event.
        That means that the earlier the event is happening, the higher the priority.
    """

    time: int = 0
    requests: List[Request] = None
    agents: Dict[Agent_Type, List] = None
    vehicles: List[Vehicle] = None
    vehicle_matrices: Dict[str, np.ndarray] = None
    events: EventQueue = None
    event_logger: EventLogger = EventLogger()
    step_size: int = 0

    def step(self):
        # self.events.print_all_events()
        if(not self.events.empty()):
            self.time += self.step_size
            print(f"Time: {self.time}")
            while(True):
                if (self.events.empty()):
                    print("No more events to process")
                    return None
                top_event : Event = self.events.peek()
                if(self.time >= top_event.timestamp):
                    event = self.events.get()
                    self.process_event(event)
                else:
                    break
        else:
            print("No more events to process")
            return None
        print(self.vehicle_matrices["Truck"])
        return self.vehicle_matrices
    
    def process_event(self, event: Event):
        if(event.type == Event_Type.ARRIVED_REQUEST):
            self.spawn_vehicle(event)
        elif(event.type == Event_Type.DISPATCH_VEHICLE):
            self.dispatch_vehicle(event)
        elif(event.type == Event_Type.DELIVER):
            self.deliver(event)

        self.event_logger.save_event(event)

    def spawn_vehicle(self, event: Event):
        request_id = event.request_id
        request : Request = self.requests[request_id]
        shipper_id = request.selected_shipper
        shipper : Shipper = self.agents[Agent_Type.SHIPPER][shipper_id]
        origin = request.origin

        delivery_time = shipper.contact_lsps(request)

        delivery_event = Event(self.time + delivery_time + 1, Event_Type.DELIVER, request_id)
        self.events.put(delivery_event)
 
        self.vehicle_matrices["Trucks"][origin][origin] += 1
        self.event_logger.save_event(event)
        # print(f"Vehicle spawned")

    def dispatch_vehicle(self, event: Event):
        request_id = event.request_id
        request: Request = self.requests[request_id]
        origin = request.origin
        destination = request.destination

        self.vehicle_matrices["Trucks"][origin][origin] -= 1
        self.vehicle_matrices["Trucks"][origin][destination] += 1
        

    def deliver(self, event: Event):
        request_id = event.request_id
        request: Request = self.requests[request_id]
        origin = request.origin
        destination = request.destination

        self.vehicle_matrices["Trucks"][origin][destination] -= 1
        self.vehicle_matrices["Trucks"][destination][destination] += 1


# ---------------------------------------------------------

def generate_and_assign_agents(num_shippers, num_lsps, num_carriers):
    
    carriers = np.empty(num_carriers, dtype=Carrier)
    lsps = np.empty(num_lsps, dtype=LSP)
    shippers = np.empty(num_shippers, dtype=Shipper)
    agents = {}

    for i in range(num_carriers):
        carriers[i] = Carrier(i)
    agents[Agent_Type.CARRIER] = carriers

    for i in range(num_lsps):
        lsps[i] = LSP(i)
    agents[Agent_Type.LSP] = lsps
    
    for i in range(num_shippers):
        shippers[i] = Shipper(i)
    agents[Agent_Type.SHIPPER] = shippers

    print("Agents generated successfully")

    # Hardcoded assignments
    agents[Agent_Type.SHIPPER][0].lsp_list = [agents[Agent_Type.LSP][0], agents[Agent_Type.LSP][1]]
    agents[Agent_Type.LSP][0].carriers = [agents[Agent_Type.CARRIER][0], agents[Agent_Type.CARRIER][1]]
    agents[Agent_Type.LSP][1].carriers = [agents[Agent_Type.CARRIER][2], agents[Agent_Type.CARRIER][3]]

    print("Agents assigned successfully")

    return agents

def generate_requests_and_events(requests_df : pd.DataFrame, dist_matrix):
    print(requests_df)
    request_size = len(requests_df)
    requests = np.empty(request_size, dtype=Request)
    events = EventQueue()


    for i in range(len(requests_df)):
        
        request_id = int(requests_df.iloc[i]['id'])
        origin = int(requests_df.iloc[i]['orig'])
        destination = int(requests_df.iloc[i]['dest'])
        volume = int(requests_df.iloc[i]['amount'])
        # price = int(requests_df.iloc[i]['price'])
        time_window: Tuple[int, int] = (int(requests_df.iloc[i]['lw']), int(requests_df.iloc[i]['uw']))
        selected_shipper = int(requests_df.iloc[i]['selected']) - 1

        distance = dist_matrix[origin][destination]
        
        new_request = Request(
                id=request_id, origin=origin, 
                destination=destination, volume=volume, time_window=time_window, 
                selected_shipper=selected_shipper, distance=distance)
        
        requests[i] = new_request

        spawn_vehicle_event = Event(time_window[0] - 1, Event_Type.ARRIVED_REQUEST, request_id)
        dispatch_vehicle_event = Event(time_window[0], Event_Type.DISPATCH_VEHICLE, request_id)
        events.put(spawn_vehicle_event)
        events.put(dispatch_vehicle_event)

    print("Requests and events created successfully")
    return requests, events

def generate_vehicles(vehicles_df: pd.DataFrame, vehicle_matrices: Dict[str, np.ndarray]):
    vehicles_size = len(vehicles_df)
    vehicles = np.empty(vehicles_size, dtype=Vehicle)

    for i in range(vehicles_size):

        vehicle_id = int(vehicles_df.iloc[i]['id'])
        name = vehicles_df.iloc[i]['name']
        initial_location = (int(vehicles_df.iloc[i]['initial_location']), int(vehicles_df.iloc[i]['initial_location']))
        max_containers = int(vehicles_df.iloc[i]['max_containers'])
        unit_cost = float(vehicles_df.iloc[i]['unit_cost'])
        emission_factor = float(vehicles_df.iloc[i]['emission_factor'])

        if name == "Truck":
            vehicle = Truck(vehicle_id, name, current_location=initial_location, max_containers=max_containers, unit_cost=unit_cost, emission_factor=emission_factor)
        if name == "Train":
            vehicle = Train(vehicle_id, name, current_location=initial_location, max_containers=max_containers, unit_cost=unit_cost, emission_factor=emission_factor)
        if name == "Barge":
            vehicle = Barge(vehicle_id, name, current_location=initial_location, max_containers=max_containers, unit_cost=unit_cost, emission_factor=emission_factor)
        
        vehicles[i] = vehicle
        vehicle_matrices[name][initial_location[0]][initial_location[1]] += 1
        
    print("Vehicles generated successfully")
    return vehicles
# ---------------------------------------------------------


def build_environment(requests_df: pd.DataFrame, nodes_df: pd.DataFrame, dist_matrix: np.ndarray, vehicles_df: pd.DataFrame, step_size: int):

    number_of_nodes = len(nodes_df)

    vehicle_matrices = {
        "Truck": np.zeros((number_of_nodes, number_of_nodes), dtype=int),
        "Train": np.zeros((number_of_nodes, number_of_nodes), dtype=int),
        "Barge": np.zeros((number_of_nodes, number_of_nodes), dtype=int),
        "Container": np.zeros((number_of_nodes, number_of_nodes), dtype=int),
    }

    agents = generate_and_assign_agents(num_shippers, num_lsps, num_carriers)
    requests, events = generate_requests_and_events(requests_df, dist_matrix)
    vehicles = generate_vehicles(vehicles_df, vehicle_matrices)

    print("Environment built successfully")

    return Environment(requests=requests, agents=agents, vehicles=vehicles,
                       vehicle_matrices=vehicle_matrices, events=events, step_size=step_size)

