import queue
import time

from dataclasses import dataclass
import random
import numpy as np
from typing import List, Tuple

CONTAINER_CAPACITY = 24

# request id is going to be -1 if the service is not associated with a request
# a truck would contain a list of services assigned by the research algorithms
class TruckService:
    def __init__(self, priority, origin, destination, request_id):
        self.priority = priority
        self.origin = origin
        self.destination = destination
        self.request_id = request_id
    
    def __lt__(self, other: 'TruckService'):
        return self.priority < other.priority
    
class TruckServiceQueue(queue.PriorityQueue):
    def peek(self):
        if self.empty():
            return None
        return self.queue[0]
    
    def print_all_events(self):
        print("Services in the queue:")
        for service in self.queue:
            print(service)

@dataclass
class Container:
    container_id: int
    contents: Tuple[int, int]
    consolidated: bool
    capacity = CONTAINER_CAPACITY

    # The research algorithms will be assumed to always produce feasible results
    def load_container(self, request: int, quantity: int):
        if request in self.contents:
            self.contents[request] += quantity
        else:
            self.contents[request] = quantity
        return True

@dataclass
class Vehicle:
    vehicle_id: int
    name: str
    current_location: Tuple[int, int]
    max_containers: int 
    unit_cost: float
    emission_factor: float 
    carrier_id: int
    number_of_containers: int = 0
    containers: List[Container] = None
    

    def __post_init__(self):
        self.contaiers = np.empty(self.max_containers, dtype=Container)

    def load_vehicle(self, container: Container):
        if self.number_of_containers < len(self.containers):
            self.containers[self.number_of_containers] = container
            self.number_of_containers += 1
            return True
        return False

    def unload_container(self, container_id: int):
        for i in range(self.number_of_containers):
            if self.containers[i].container_id == container_id:
                self.containers[i] = None
                self.number_of_containers -= 1
                return True
        return False

@dataclass
class Truck(Vehicle):
    services: TruckServiceQueue = TruckServiceQueue()
    depot: int = -1                             
    long_haul: bool = True
    speed_per_timestep: int = random.randint(40, 60) # km/h

@dataclass
class Train(Vehicle):
    pass
    
@dataclass
class Barge(Vehicle):
    pass