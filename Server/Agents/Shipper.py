from Agents.Misc import Request
import Simulation

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
            selected_lsp, quote = lsp.process_request(env, request)
            quotes.append((selected_lsp, quote))
        # selected_lsp, quote = min(quotes, key=lambda x: (yield x[1])[1])
        
        # Schedule truck dispatch when time-window starts
        yield env.timeout(request.time_window[0] - env.now)