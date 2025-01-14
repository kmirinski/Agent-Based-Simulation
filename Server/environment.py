import queue
import numpy as np
import pandas as pd

from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Dict

from agents import Shipper, LSP, Carrier

from common import Vehicle, Request, Event, Event_Type, Agent_Type

num_shippers = 1
num_lsps = 2
num_carriers = 4

class EventQueue(queue.PriorityQueue):
    def peek(self):
        if self.empty():
            return None
        return self.queue[0]
    
    def print_all_events(self):
        print("Events in the queue:")
        for event in self.queue:
            print(event)

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
    vehicle_matrix: Dict[str, np.ndarray] = None
    events: EventQueue = None

    def step(self):
        # self.events.print_all_events()
        if(not self.events.empty()):
            self.time += 1
            print(f"Time: {self.time}")
            top_event : Event = self.events.peek()
            if(self.time == top_event.timestamp):
                event = self.events.get()
                self.process_event(event)
        else:
            print("No events in the queue. Simulation ended.")

        # print(self.vehicle_matrix["Trucks"])
        return self.vehicle_matrix
    
    def step_to_next_event(self):
        if not self.event_queue.empty():
            earliest_event = self.event_queue.peek()
            earliest_event_time = earliest_event[0]
            if(earliest_event_time > self.time):
                self.time = earliest_event_time
                event = self.event_queue.get()
                self.process_event(self, event)
    
    def process_event(self, event: Event):
        if(event.type == Event_Type.SPAWN_VEHICLE):
            self.spawn_vehicle(event)
            print("Spawn vehicle event")
        elif(event.type == Event_Type.DISPATCH_VEHICLE):
            self.dispatch_vehicle(event)
            print("Dispatch vehicle event")
        elif(event.type == Event_Type.DELIVER):
            self.deliver(event)
            print("Deliver vehicle event")
        else:
            print("Unknown event type")

    def spawn_vehicle(self, event: Event):
        request_id = event.request_id
        request : Request = self.requests[request_id]
        shipper_id = request.selected_shipper
        shipper : Shipper = self.agents[Agent_Type.SHIPPER][shipper_id]
        origin = request.origin

        delivery_time = shipper.contact_lsps(request)

        delivery_event = Event(self.time + delivery_time + 1, Event_Type.DELIVER, request_id)
        self.events.put(delivery_event)
 
        self.vehicle_matrix["Trucks"][origin][origin] += 1
        print(f"Vehicle spawned")

    def dispatch_vehicle(self, event):
        request_id = event.request_id
        request : Request = self.requests[request_id]
        origin = request.origin
        destination = request.destination

        self.vehicle_matrix["Trucks"][origin][origin] -= 1
        self.vehicle_matrix["Trucks"][origin][destination] += 1
        print(f"Vehicle dispatched")

    def deliver(self, event):
        request_id = event.request_id
        request : Request = self.requests[request_id]
        origin = request.origin
        destination = request.destination

        self.vehicle_matrix["Trucks"][origin][destination] -= 1
        self.vehicle_matrix["Trucks"][destination][destination] += 1
        print(f"Vehicle delivered")



def generate_and_assign_agents(num_shippers, num_lsps, num_carriers):
    
    carriers = []
    lsps = []
    shippers = []
    agents = {}

    for i in range(num_carriers):
        carriers.append(Carrier(i))
    agents[Agent_Type.CARRIER] = carriers

    for i in range(num_lsps):
        lsps.append(LSP(i))
    agents[Agent_Type.LSP] = lsps
    
    for i in range(num_shippers):
        shippers.append(Shipper(i))
    agents[Agent_Type.SHIPPER] = shippers

    print("Agents generated successfully")

    agents[Agent_Type.SHIPPER][0].lsp_list = [agents[Agent_Type.LSP][0], agents[Agent_Type.LSP][1]]
    agents[Agent_Type.LSP][0].carriers = [agents[Agent_Type.CARRIER][0], agents[Agent_Type.CARRIER][1]]
    agents[Agent_Type.LSP][1].carriers = [agents[Agent_Type.CARRIER][2], agents[Agent_Type.CARRIER][3]]
    print(f'AAAAAAAAAAA: {type(agents[Agent_Type.SHIPPER][0].lsp_list[0])}')

    print("Agents assigned successfully")

    return agents


def create_requests_and_events(requests_df, dist_matrix):
    print(requests_df)
    requests = []
    events = EventQueue()

    for i in range(len(requests_df)):
        
        request_id = int(requests_df.iloc[i]['id'])
        origin = int(requests_df.iloc[i]['orig'])
        destination = int(requests_df.iloc[i]['dest'])
        amount = int(requests_df.iloc[i]['amount'])
        price = int(requests_df.iloc[i]['price'])
        time_window: Tuple[int, int] = (int(requests_df.iloc[i]['lw']), int(requests_df.iloc[i]['uw']))
        selected_shipper = int(requests_df.iloc[i]['selected']) - 1

        distance = dist_matrix[origin][destination]
        
        new_request = Request(
                id=request_id, origin=origin, 
                destination=destination, amount=amount, 
                price=price, time_window=time_window, 
                selected_shipper=selected_shipper, distance=distance)
        
        requests.append(new_request)

        spawn_vehicle_event = Event(time_window[0] - 1, Event_Type.SPAWN_VEHICLE, request_id)
        dispatch_vehicle_event = Event(time_window[0], Event_Type.DISPATCH_VEHICLE, request_id)
        events.put(spawn_vehicle_event)
        events.put(dispatch_vehicle_event)

    print("Requests and events created successfully")
    return requests, events

def build_environment(requests_df: pd.DataFrame, nodes_df: pd.DataFrame, dist_matrix: np.ndarray):
    
    agents = generate_and_assign_agents(num_shippers, num_lsps, num_carriers)
    requests, events = create_requests_and_events(requests_df, dist_matrix)
    number_of_nodes = len(nodes_df)

    vehicle_matrix = {
        "Trucks": np.zeros((number_of_nodes, number_of_nodes), dtype=int),
    }

    print("Environment built successfully")

    return Environment(requests=requests, agents=agents, 
                       vehicle_matrix=vehicle_matrix, events=events)

def get_snapshot(env: Environment):
    return env.step()

