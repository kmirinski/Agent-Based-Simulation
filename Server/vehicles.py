from enum import Enum
import queue

from dataclasses import dataclass, field
import random
from typing import Dict, List, Tuple

CONTAINER_CAPACITY = 24

class VehicleStatus(Enum):
    IDLE = 0
    EN_ROUTE = 1
    LOADING = 2
    UNLOADING = 4


# request id is going to be -1 if the service is not associated with a request
# a truck would contain a list of services assigned by the research algorithms
class Service:
    def __init__(self, origin, destination, departure_time, 
                 arrival_time, cost, capacity, vehicle_id, remaining_distance):
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.cost = cost
        self.capacity = capacity
        self.vehicle_id = vehicle_id
        self.remaining_distance = remaining_distance
        self.requests = []
    
    def __lt__(self, other: 'Service'):
        return self.departure_time < other.departure_time

    
class ServiceQueue(queue.PriorityQueue):
    def peek(self):
        if self.empty():
            return None
        return self.queue[0]
    
    def print_all_events(self):
        print("Services in the queue:")
        for service in self.queue:
            print(service)

# @dataclass
# class Container:
#     container_id: int
#     current_location: Tuple[int, int]
#     load: int = 0
#     consolidated: bool = True
#     capacity = CONTAINER_CAPACITY

#     # The research algorithms will be assumed to always produce feasible results
#     def load_container(self, amount: int) -> bool:
#         if self.load + amount <= self.capacity:
#             self.load += amount
#             return True
#         return False

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
    services: ServiceQueue = ServiceQueue()
    containers: Dict[int, int] = field(default_factory=dict)            # Key is request id, value is quantity
    status: VehicleStatus = VehicleStatus.IDLE


    def load_vehicle(self, request_id: int, amount: int) -> bool:
        if self.number_of_containers < self.max_containers:
            if request_id in self.containers:
                self.containers[request_id] += amount
            else:
                self.containers[request_id] = amount
            self.number_of_containers += 1
            return True
        else:
            return False

    def unload_container(self, container_id: int):
        for i in range(self.number_of_containers):
            if self.containers[i].container_id == container_id:
                self.containers[i] = None
                self.number_of_containers -= 1
                return True
        return False
    
    def to_dict(self):
        """
        Convert the Vehicle object to a dictionary representation.
        
        Returns:
            dict: A dictionary representation of the Vehicle object.
        """
        return {
            "vehicle_id": self.vehicle_id,
            "name": self.name,
            "current_location": self.current_location,
            "max_containers": self.max_containers,
            "unit_cost": self.unit_cost,
            "emission_factor": self.emission_factor,
            "carrier_id": self.carrier_id,
            "number_of_containers": self.number_of_containers,
            "containers": dict(self.containers),
            "status": self.status.name
        }

@dataclass
class Truck(Vehicle):
    depot: int = -1                             
    long_haul: bool = True
    speed_per_timestep: int = random.randint(40, 60) # km/h

@dataclass
class Train(Vehicle):
    pass

@dataclass
class Barge(Vehicle):
    pass