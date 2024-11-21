from Agents.Misc import Truck

class LSP:
    def __init__(self, id):
        self.id = id
        self.carriers = []
        self.containers_not_departed = []
        self.containers_in_transit = []
        self.containers_delivered = []

    def process_request(self, env, request):
        # Ask carriers for quotes and select the cheapest
        quotes = [(carrier, carrier.quote(request)) for carrier in self.carriers]
        selected_carrier, price = min(quotes, key=lambda x: x[1])
        price_with_margin = price * 1.10  # Adding 10% margin

        # Track accepted container
        self.containers_not_departed.append(request)
        
        # # Notify shipper after 1 hour (delay for the quote process)
        # yield env.timeout(1)
        return selected_carrier, price_with_margin

    def dispatch_truck(self, env, request, carrier):
        self.containers_not_departed.remove(request)
        truck = Truck(carrier, request, request.distance)
        self.containers_in_transit.append(request)

        # Simulate truck travel
        yield env.timeout(truck.travel_time)

        # Truck arrived
        self.containers_in_transit.remove(request)
        self.containers_delivered.append(request)
        carrier.assign_container(request, request.distance, truck.travel_time)