from Agents.Misc import Request
from Simulation.Global import lsps

class Shipper:
    def __init__(self, id):
        self.id = id
        self.lsp_list = []
        self.requests = []

    def process_dispatch_request(self, env, request):

        # Ask  LSPs for quotes and select the cheapest offer
        print(f"Time now: {env.now}, Time window: {request.time_window}")
        quotes = []
        print("Shipper rules!")
        for lsp in self.lsp_list:
            selected_carrier, quote = lsp.process_request(env, request)
            quotes.append((selected_carrier, quote))
        
        selected_lsp = min(quotes, key=lambda x: x[1])[0]

        lsps[selected_lsp].initiate_truck(env, request)

        # Schedule truck dispatch when time-window starts
        yield env.timeout(request.time_window[0] - env.now)

    def delivered_request(self, env, request):
        print(f"Request {request.id} delivered at time {env.now}")
        self.requests.remove(request)