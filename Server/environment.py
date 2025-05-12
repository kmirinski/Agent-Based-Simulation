import queue
import numpy as np
import pandas as pd

from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Dict

from agents import Shipper, LSP, Carrier
from data_logger import EventLogger, EnvironmentStateLogger

from common import Request, Event, Event_Type, Agent_Type
from vehicles import Service, Truck, Train, Barge, Vehicle, VehicleStatus

# ---------------------------------------------------------


num_shippers = 1
num_lsps = 2
num_carriers = 4

load_time = 1

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
    state_logger: EnvironmentStateLogger = EnvironmentStateLogger()
    step_size: int = 0

    def step(self):
        self.events.print_all_events()
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
                    self.state_logger.save_state(self.time, self.vehicle_matrices, self.vehicles)
                    break
        else:
            print("No more events to process")
            return None
        # print([vehicle.vehicle_id for vehicle in self.agents[Agent_Type.CARRIER][0].fleet])
        # print(self.vehicle_matrices["Train"])
        return self.vehicle_matrices
    
    def process_event(self, event: Event):
        event_handlers = {
            Event_Type.REQUEST_ARRIVED: self.request_arrived,
            Event_Type.REQUEST_COMPLETED: self.request_completed,
            Event_Type.TRUCK_DEPARTED: self.vehicle_departed,
            Event_Type.TRAIN_DEPARTED: self.vehicle_departed,
            Event_Type.BARGE_DEPARTED: self.vehicle_departed,
            Event_Type.TRUCK_ARRIVED: self.vehicle_arrived,
            Event_Type.TRAIN_ARRIVED: self.vehicle_arrived,
            Event_Type.BARGE_ARRIVED: self.vehicle_arrived
        }
        
        handler = event_handlers.get(event.type)
        if handler:
            handler(event)
        else:
            raise ValueError(f"No handler for event type: {event.type}")


    def request_arrived(self, event: Event):
        request_id = event.request_id
        request : Request = self.requests[request_id]

        shipper_id = request.selected_shipper
        shipper : Shipper = self.agents[Agent_Type.SHIPPER][shipper_id]

        # RUN THE DECISION MAKING ALGORITHM TO DECIDE WHICH VEHICLES WILL EXECUTE THIS REQUEST
        #############################################
        # delivery_time = shipper.contact_lsps(request)

        vehicles_to_depart: List[Tuple[int, int, int]] = shipper.decision_making(request)
        #############################################

        request.services += len(vehicles_to_depart)

        for vehicle_id, amount, timestamp in vehicles_to_depart:
            vehicle: Vehicle = self.vehicles[vehicle_id]
            vehicle.status = VehicleStatus.LOADING
            self.spawn_containers(request, vehicle_id, amount)
            new_event = Event(timestamp + load_time, self.choose_departed_event(vehicle), request_id=request_id, vehicle_id=vehicle_id)
            self.events.put(new_event)

            ## FIX FOR TRUCKS ## FIX FOR ALL!!!!!
            
        print(f"Request arrived: {request_id} - {request.origin} -> {request.destination}")

    def request_completed(self, event: Event):
        request_id = event.request_id

        # Last vehicle to arrive for the request
        vehicle_id = event.vehicle_id
        vehicle = self.vehicles[vehicle_id]
        vehicle.status = VehicleStatus.IDLE
        print(f"Request {request_id} completed at time {self.time}")
        
        

    def vehicle_departed(self, event: Event):
        vehicle_id = event.vehicle_id
        request_id = event.request_id

        request: Request = self.requests[request_id]
        vehicle: Vehicle = self.vehicles[vehicle_id]

        destination = request.destination
        origin = request.origin

        # Update location
        self.vehicle_matrices[vehicle.name][origin][origin] -= 1
        self.vehicle_matrices[vehicle.name][origin][destination] += 1
        self.vehicle_matrices["Container"][origin][origin] -= vehicle.number_of_containers
        self.vehicle_matrices["Container"][origin][destination] += vehicle.number_of_containers
        vehicle.current_location = [origin, destination]
        
        # Update status
        vehicle.status = VehicleStatus.EN_ROUTE
        print(f"Vehicle {vehicle_id} departed from {origin} for request {request_id} at time {self.time}")

    def vehicle_arrived(self, event: Event):
        request_id = event.request_id
        vehicle_id = event.vehicle_id

        request: Request = self.requests[request_id]
        vehicle: Vehicle = self.vehicles[vehicle_id]
        
        origin = request.origin
        destination = request.destination

        # Update location
        self.vehicle_matrices[vehicle.name][origin][destination] -= 1
        self.vehicle_matrices[vehicle.name][destination][destination] += 1
        self.vehicle_matrices["Container"][origin][destination] -= vehicle.number_of_containers
        self.vehicle_matrices["Container"][destination][destination] += vehicle.number_of_containers
        vehicle.current_location = [destination, destination]

        # Update status
        vehicle.status = VehicleStatus.UNLOADING
        vehicle.services.get()
        request.services -= 1

        if request.is_request_fulfilled():
            new_event = Event(self.time + load_time, Event_Type.REQUEST_COMPLETED, request_id=request_id, vehicle=vehicle)
            self.events.put(new_event)

        
        print(f"Vehicle {vehicle_id} arrived at {destination} for request {request_id} at time {self.time}")
        
    def spawn_containers(self, vehicle: Vehicle, request_id: int, amount: int):
        # Algorithm ensures that the vehicle has enough capacity for the amount
        number_of_containers = amount // 24 + 1
        vehicle.load_vehicle(request_id, number_of_containers)
        self.vehicle_matrices["Container"][vehicle.current_location[0]][vehicle.current_location[1]] += number_of_containers

    def choose_arrived_event(self, vehicle: Vehicle):
        if isinstance(vehicle, Truck):
            return Event_Type.TRUCK_ARRIVED
        elif isinstance(vehicle, Train):
            return Event_Type.TRAIN_ARRIVED
        elif isinstance(vehicle, Barge):
            return Event_Type.BARGE_ARRIVED
        else:
            raise ValueError("Unknown vehicle type")

    def choose_departed_event(self, vehicle: Vehicle):
        if isinstance(vehicle, Truck):
            return Event_Type.TRUCK_DEPARTED
        elif isinstance(vehicle, Train):
            return Event_Type.TRAIN_DEPARTED
        elif isinstance(vehicle, Barge):
            return Event_Type.BARGE_DEPARTED
        else:
            raise ValueError("Unknown vehicle type")


        
        

# ---------------------------------------------------------

def generate_vehicles(vehicles_df: pd.DataFrame, vehicle_matrices: Dict[str, np.ndarray], vehicle_list_: List[Vehicle]):
    vehicles_size = len(vehicles_df)

    for i in range(vehicles_size):

        vehicle_id = int(vehicles_df.iloc[i]['id'])
        name = vehicles_df.iloc[i]['name']
        initial_location = (int(vehicles_df.iloc[i]['initial_location']), int(vehicles_df.iloc[i]['initial_location']))
        max_containers = int(vehicles_df.iloc[i]['max_containers'])
        unit_cost = float(vehicles_df.iloc[i]['unit_cost'])
        emission_factor = float(vehicles_df.iloc[i]['emission_factor'])
        carrier_id = int(vehicles_df.iloc[i]['carrier_id'])

        if name == "Truck":
            vehicle = Truck(vehicle_id, name, current_location=initial_location, max_containers=max_containers, 
                            unit_cost=unit_cost, emission_factor=emission_factor, carrier_id=carrier_id)
        if name == "Train":
            vehicle = Train(vehicle_id, name, current_location=initial_location, max_containers=max_containers, 
                            unit_cost=unit_cost, emission_factor=emission_factor, carrier_id=carrier_id)
        if name == "Barge":
            vehicle = Barge(vehicle_id, name, current_location=initial_location, max_containers=max_containers, 
                            unit_cost=unit_cost, emission_factor=emission_factor, carrier_id=carrier_id)
        
        vehicle_list_[i] = vehicle
        vehicle_matrices[name][initial_location[0]][initial_location[1]] += 1
        
    print("Vehicles generated successfully")

def generate_services_and_events(services_df: pd.DataFrame, dist_matrix: np.ndarray, vehicles: List[Vehicle], event_queue: EventQueue):
    services_size = len(services_df)

    for i in range(services_size):
        origin = int(services_df.iloc[i]['origin'])
        destination = int(services_df.iloc[i]['destination'])
        departure_time = float(services_df.iloc[i]['departure_time'])
        arrival_time = float(services_df.iloc[i]['arrival_time'])
        cost = float(services_df.iloc[i]['cost'])
        capacity = int(services_df.iloc[i]['capacity'])
        vehicle_id = int(services_df.iloc[i]['vehicle_id'])
        remaining_distance = dist_matrix[origin][destination]

        new_service = Service(
            origin=origin, destination=destination, departure_time=departure_time, 
            arrival_time=arrival_time, cost=cost, capacity=capacity, 
            vehicle_id=vehicle_id, remaining_distance=remaining_distance)
        
        # Check the vehicle ID - might need to change the Event class
        departure_event = Event(departure_time, type=Event_Type.TRAIN_DEPARTED, vehicle_id=vehicle_id)
        arrival_event = Event(arrival_time, type=Event_Type.TRAIN_ARRIVED, vehicle_id=vehicle_id)
        event_queue.put(departure_event)
        event_queue.put(arrival_event)

        vehicles[vehicle_id].services.put(new_service)

    print("Services generated successfully")

def generate_and_assign_agents(num_shippers: int, num_lsps: int, num_carriers: int, 
                               vehicles: List[Vehicle], agent_dict: Dict[Agent_Type, List]):
    
    carriers = np.empty(num_carriers, dtype=Carrier)
    lsps = np.empty(num_lsps, dtype=LSP)
    shippers = np.empty(num_shippers, dtype=Shipper)

    for i in range(num_carriers):
        carriers[i] = Carrier(i)
    agent_dict[Agent_Type.CARRIER] = carriers

    for i in range(num_lsps):
        lsps[i] = LSP(i)
    agent_dict[Agent_Type.LSP] = lsps
    
    for i in range(num_shippers):
        shippers[i] = Shipper(i)
    agent_dict[Agent_Type.SHIPPER] = shippers

    print("Agents generated successfully")

    # Hardcoded assignments
    agent_dict[Agent_Type.SHIPPER][0].lsp_list = [agent_dict[Agent_Type.LSP][0], agent_dict[Agent_Type.LSP][1]]
    agent_dict[Agent_Type.LSP][0].carriers = [agent_dict[Agent_Type.CARRIER][0], agent_dict[Agent_Type.CARRIER][1]]
    agent_dict[Agent_Type.LSP][1].carriers = [agent_dict[Agent_Type.CARRIER][2], agent_dict[Agent_Type.CARRIER][3]]

    for vehicle in vehicles:
        vehicle_carrier_id = vehicle.carrier_id
        agent_dict[Agent_Type.CARRIER][vehicle_carrier_id].fleet.append(vehicle)

    print("Agents assigned successfully")

def generate_requests_and_events(requests_df : pd.DataFrame, dist_matrix, requests: List[Request], events: EventQueue):

    for i in range(len(requests_df)):
        
        request_id = int(requests_df.iloc[i]['id'])
        origin = int(requests_df.iloc[i]['orig'])
        destination = int(requests_df.iloc[i]['dest'])
        amount = int(requests_df.iloc[i]['amount'])
        # price = int(requests_df.iloc[i]['price'])
        time_window: Tuple[int, int] = (int(requests_df.iloc[i]['lw']), int(requests_df.iloc[i]['uw']))
        selected_shipper = int(requests_df.iloc[i]['selected']) - 1

        distance = dist_matrix[origin][destination]
        
        new_request = Request(
                id=request_id, origin=origin, 
                destination=destination, amount=amount, time_window=time_window, 
                selected_shipper=selected_shipper, distance=distance)
        
        requests[i] = new_request   

        arrived_request_event = Event(time_window[0], Event_Type.REQUEST_ARRIVED, request_id=request_id)
        events.put(arrived_request_event) 

    print("Requests and events created successfully")


# ---------------------------------------------------------

def build_environment(requests_df: pd.DataFrame, nodes_df: pd.DataFrame, 
                      dist_matrix: np.ndarray, vehicles_df: pd.DataFrame, 
                      services_df: pd.DataFrame, step_size: int):
    
    vehicle_list = np.empty(len(vehicles_df), dtype=Vehicle)
    request_list = np.empty(len(requests_df), dtype=Request)
    agent_dict = {}
    event_queue = EventQueue()

    number_of_nodes = len(nodes_df)
    vehicle_matrices = {
        "Truck": np.zeros((number_of_nodes, number_of_nodes), dtype=int),
        "Train": np.zeros((number_of_nodes, number_of_nodes), dtype=int),
        "Barge": np.zeros((number_of_nodes, number_of_nodes), dtype=int),
        "Container": np.zeros((number_of_nodes, number_of_nodes), dtype=int),
    }

    generate_vehicles(vehicles_df, vehicle_matrices, vehicle_list)
    generate_services_and_events(services_df, dist_matrix, vehicle_list, event_queue)
    generate_and_assign_agents(num_shippers, num_lsps, num_carriers, vehicle_list, agent_dict)
    generate_requests_and_events(requests_df, dist_matrix, request_list, event_queue)

    print("Environment built successfully")

    return Environment(requests=request_list, agents=agent_dict, vehicles=vehicle_list,
                       vehicle_matrices=vehicle_matrices, events=event_queue, step_size=step_size)

