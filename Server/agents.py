import random
import math
from typing import List, Tuple

from common import Vehicle, Request

class Carrier:
    def __init__(self, id):
        self.id = id
        self.vehicles: List[Vehicle] = []
        self.price_per_hour = 10

    def quota(self, request: Request) -> Tuple[float, float]:
        distance = request.distance
        speed = 60 + random.randint(-10, 10)
        time = distance / speed
        price = time * self.price_per_hour
        time = int(math.ceil(time))
        return price, time 
    
class LSP:
    def __init__(self, id):
        self.id = id
        self.carriers: List[Carrier] = []

    def contact_carriers(self, request: Request) -> Tuple[int, float, float]:
        best_carrier = None
        best_quota = None

        for carrier in self.carriers:
            quota = carrier.quota(request) 
            if best_quota is None or quota[0] < best_quota[0]: 
                best_carrier = carrier
                best_quota = quota

        price, time = best_quota
        return best_carrier.id, self.id, price, time
    
class Shipper:
    def __init__(self, id):
        self.id = id
        self.lsp_list: List[LSP] = []

    def contact_lsps(self, request: Request) -> Tuple[int, float, float]:
        best_offer = None
        best_price = None

        for lsp in self.lsp_list:
            carrier_id, lsp_id, price, time = lsp.contact_carriers(request)
            if best_price is None or price < best_price:
                best_price = price
                best_offer = (carrier_id, lsp_id, price, time)
        print(f"Best offer: {best_offer}")
        return best_offer[3] 

    def contact_carrier(self, request: Request):
        pass


        