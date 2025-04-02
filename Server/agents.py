import random
import math
import numpy as np
from typing import List, Tuple

from common import Request
from vehicles import Vehicle, VehicleStatus

class Carrier:
    """
    A carrier is an agent that has a fleet of vehicles and can provide transportation services.
    The fleet stores the ids of the vehicles in the fleet.
    """
    def __init__(self, id):
        self.id = id
        self.fleet: List[Vehicle] = []

    def quota(self, request: Request) -> Tuple[float, float]:
        distance = request.distance
        min_price = float('inf')
        best_time = None

        for vehicle in self.fleet:
            time = distance / vehicle.speed_per_timestep
            price = time * vehicle.unit_cost
            if price < min_price:
                min_price = price
                best_time = time

        return min_price, best_time
    
class LSP:
    """"
    A logistics service provider (LSP) is an agent that can contact carriers to provide transportation services."
    """
    def __init__(self, id):
        self.id = id
        self.carriers: List[Carrier] = np.empty(0, dtype=Carrier)

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
    """"
    A shipper is an agent that can send requests to LSPs to provide transportation services."
    """
    def __init__(self, id):
        self.id = id
        self.lsp_list: List[LSP] = np.empty(0, dtype=LSP)
        self.requests: List[Request] = np.empty(0, dtype=Request)

    def contact_lsps(self, request: Request) -> Tuple[int, float, float]:
        best_offer = None
        best_price = None

        for lsp in self.lsp_list:
            carrier_id, lsp_id, price, time = lsp.contact_carriers(request)
            if best_price is None or price < best_price:
                best_price = price
                best_offer = (carrier_id, lsp_id, price, time)
        return best_offer[3]

        