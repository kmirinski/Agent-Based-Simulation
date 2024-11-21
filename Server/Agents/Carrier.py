import random
from Agents.Misc import Truck


class Carrier:
    def __init__(self, id):
        self.id = id
        self.assigned_containers = []
        self.total_distance = 0
        self.total_travel_time = 0
    
    def initiate_truck(self, request):
        truck = Truck(self, request.id, request.distance)
        truck.estimate_time()
        # if the price is 100 per hour
        return truck * 100

    def assign_container(self, container, distance, travel_time):
        self.assigned_containers.append(container)
        self.total_distance += distance
        self.total_travel_time += travel_time