from enum import Enum
import queue

from dataclasses import dataclass, field
import random
from typing import List, Tuple

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
    
    def to_dict(self):
        return {
            "container_id": self.container_id,
            "contents": self.contents,
            "consolidated": self.consolidated
        }

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
    containers: list = field(default_factory=list)
    status: VehicleStatus = VehicleStatus.IDLE


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
            "containers": [container.to_dict() for container in self.containers if container is not None],
            "status": self.status.name
        }

@dataclass
class Truck(Vehicle):
    depot: int = -1                             
    long_haul: bool = True
    speed_per_timestep: int = random.randint(40, 60) # km/h

@dataclass
class Train(Vehicle):
    predefined_schedule: List[Tuple[int, int]] = None
    
@dataclass
class Barge(Vehicle):
    predefined_schedule: List[Tuple[int, int]] = None