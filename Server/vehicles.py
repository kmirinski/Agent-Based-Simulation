import random
import numpy as np
from typing import Dict

TRUCK_EMISSION_FACTOR = 0.05
TRUCK_UNIT_COST = 100

class Container:
    def __init__(self, container_id, consolided=False, capacity=24):
        self.container_id = container_id
        self.contents: Dict[int, int] = {}          # key: request_id, value: quantity
        self.consolidated = consolided              # This flag will be used by the algorithms
        self.capacity = capacity

    # The research algorithms will be assumed to always produce feasible results
    def load_container(self, request: int, quantity: int):
        if request in self.contents:
            self.contents[request] += quantity
        else:
            self.contents[request] = quantity
        return True


class Vehicle:
    def __init__(self, max_containers, unit_cost, emission_factor):
        self.number_of_containers = 0
        self.containers = np.empty(max_containers, dtype=Container)
        self.unit_cost = unit_cost
        self.emission_factor = emission_factor

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
        

    def is_full(self):
        return self.number_of_containers == len(self.containers)

    def is_empty(self):
        return self.number_of_containers == 0
    
class Truck(Vehicle):
    def __init__(
            self, 
            depot: int,                             # ID of the depot - can be fetched from the network 
            long_haul: bool = True,                 # True if the truck is long haul, False if it is local -> has to return to depot if local
            max_containers=1,                       # The truck can carry at most one container
            unit_cost=TRUCK_UNIT_COST,              # Cost per unit 
            emission_factor=TRUCK_EMISSION_FACTOR   # Emission factor 
        ):

        super().__init__(max_containers, unit_cost, emission_factor)
        self.depot = depot
        self.long_haul = long_haul
        self.speed = random.randint(40, 60)

class Barge(Vehicle):
    def __init__(
            self,  
            max_containers=1,                       # The truck can carry at most one container
            unit_cost=TRUCK_UNIT_COST,              # Cost per unit 
            emission_factor=TRUCK_EMISSION_FACTOR   # Emission factor 
        ):

        super().__init__(max_containers, unit_cost, emission_factor)

class Train(Vehicle):
    def __init__(
            self, 
            max_containers=1,                       # The truck can carry at most one container
            unit_cost=TRUCK_UNIT_COST,              # Cost per unit 
            emission_factor=TRUCK_EMISSION_FACTOR   # Emission factor 
        ):

        super().__init__(max_containers, unit_cost, emission_factor)