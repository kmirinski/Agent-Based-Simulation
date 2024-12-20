from Agents.Misc import Truck
from Simulation.Global import *

class LSP:
    def __init__(self, id):
        self.id = id
        self.carriers = []
        self.containers_not_departed = []
        self.containers_in_transit = []
        self.containers_delivered = []

    def process_request(self, env, request):
        # Ask carriers for quotes and select the cheapest
        # print("LSP rules!")
        quotes = [(carrier.id, carrier.quota(env, request)) for carrier in self.carriers]
        selected_carrier, price = min(quotes, key=lambda x: x[1])

        # # Track accepted container
        # self.containers_not_departed.append(request)

        return selected_carrier, price
    
    def initiate_truck(self, env, request):
        truck = Truck(self, request.id, request.distance)
        truck.estimate_time(env)