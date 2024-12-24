from Agents.Misc import Request

class Shipper:
    def __init__(self, id):
        self.id = id
        self.lsp_list = []

    def process_dispatch_request(self, env, request):

        # Ask  LSPs for quotes and select the cheapest offer
        print(f"Time now: {env.now}, Time window: {request.time_window}")
        quotes = []
        # print("Shipper rules!")
        for lsp in self.lsp_list:
            selected_carrier, quote = lsp.process_request(env, request)
            quotes.append((selected_carrier, quote))
        
        selected_lsp = min(quotes, key=lambda x: x[1])[0]

        lsps[selected_lsp].initiate_truck(env, request)
        print(f'CURRENT TIME AFTER PROCESSING: {env.now}')
        print_all_ids()
        # Schedule truck dispatch when time-window starts
        print(f'Timeout is {request.time_window[0] - env.now}')
        yield env.timeout(request.time_window[0] - env.now)

    
    def delivered_request(self, env, request):
        print(f"Request {request.id} delivered at time {env.now}")
        self.requests.remove(request)
        yield 