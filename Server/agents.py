import random

from common import Vehicle

price = 100     # We assume the price is 100 per hour

class Shipper:
    def __init__(self, id):
        self.id = id
        self.lsp_list = []

    def generate_vehicle(self, request):
        for lsp in self.lsp_list:
            pass
        
        speed = 60
        vehicle = Vehicle(name="Empty Truck", origin=request.origin,
                          destination=request.destination, quantity=1,
                          distance=request.distance, remaining_distance=request.distance,
                          speed=speed)
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
        # print("Carrier rules!")
        travel_time = request.distance / self.estimated_average_speed
        return travel_time * price