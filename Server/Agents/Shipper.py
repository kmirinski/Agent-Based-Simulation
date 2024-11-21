from Agents.Misc import Request
import Simulation

class Shipper:
    def __init__(self, id):
        self.id = id
        self.lps_list = []
        self.requests = []

    def process_dispatch_request(self, env, request):

        # Ask  LSPs for quotes and select the cheapest offer
        quotes = [()]
        quotes = [(lsp, env.process(lsp.process_request(env, request))) for lsp in self.lps_list]
        selected_lsp, quote = min(quotes, key=lambda x: (yield x[1])[1])
        
        # Schedule truck dispatch when time-window starts
        yield env.timeout(request.time_window - env.now)  # Wait until the time window starts
        carrier = yield env.process(selected_lsp.dispatch_truck(env, request, selected_lsp.carriers[0]))