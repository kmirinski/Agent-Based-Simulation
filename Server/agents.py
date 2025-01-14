import random
from typing import List, Tuple

from common import Vehicle, Request

price = 1     # We assume the price is 100 per hour

class Shipper:
    def __init__(self, id):
        self.id = id
        self.lsp_list = []

    def generate_vehicle(self, request: Request):
        quotes = []
        for lsp in self.lsp_list:
            quotes.append(lsp.process_request(request))
        
        selected_carrier, _ = min(quotes, key=lambda x: x[1])


        speed = 60
        vehicle = Vehicle(name="Empty Truck", origin=request.origin,
                          destination=request.destination, quantity=1,
                          distance=request.distance, remaining_distance=request.distance,
                          speed=speed)
        
        selected_carrier.vehicles.append(vehicle)
        return vehicle

    # def process_dispatch_request(self, env, request):

    #     # Ask  LSPs for quotes and select the cheapest offer
    #     print(f"Time now: {env.now}, Time window: {request.time_window}")
    #     quotes = []
    #     # print("Shipper rules!")
    #     for lsp in self.lsp_list:
    #         selected_carrier, quote = lsp.process_request(env, request)
    #         quotes.append((selected_carrier, quote))
        
    #     selected_lsp = min(quotes, key=lambda x: x[1])[0]

    #     lsps[selected_lsp].initiate_truck(env, request)
    #     print(f'CURRENT TIME AFTER PROCESSING: {env.now}')
    #     print_all_ids()
    #     # Schedule truck dispatch when time-window starts
    #     print(f'Timeout is {request.time_window[0] - env.now}')
    #     yield env.timeout(request.time_window[0] - env.now)

    
    # def delivered_request(self, env, request):
    #     print(f"Request {request.id} delivered at time {env.now}")
    #     self.requests.remove(request)
    #     yield 


class LSP:
    def __init__(self, id):
        self.id = id
        self.carriers = []
        self.containers_not_departed = []
        self.containers_in_transit = []
        self.containers_delivered = []

    def process_request(self, request):
        quotes = [(carrier, carrier.quota(request)) for carrier in self.carriers]
        selected_carrier, price = min(quotes, key=lambda x: x[1])


    def process_request(self, request: Request):
        # Ask carriers for quotes and select the cheapest
        # print("LSP rules!")
        
        quotes = [(carrier.id, carrier.quota(request)) for carrier in self.carriers]
        selected_carrier, price = min(quotes, key=lambda x: x[1])

        return selected_carrier, price


class Carrier:
    def __init__(self, id):
        self.id = id
        vehicles: List[Vehicle] = []

    def quota(self, request: Request):
        return price * request.distance

        