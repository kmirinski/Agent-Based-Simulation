import random
from Agents.Misc import Truck

price = 100     # We assume the price is 100 per hour

class Carrier:
    def __init__(self, id):
        self.id = id
        self.assigned_containers = []
        self.total_distance = 0
        self.total_travel_time = 0
        self.estimated_average_speed = 50         # HARDCODED
    
    # Initiates a truck to deliver and returns the price

    def quota(self, env, request):
        # print(f"Distance: {self.distance}, Average Speed: {self.average_speed}, Travel Time: {self.travel_time}")
        print("Carrier rules!")
        travel_time = request.distance / self.estimated_average_speed
        return travel_time * price