import random
import math
import numpy as np
from typing import List, Tuple

from common import Request
from vehicles import Service, Vehicle, VehicleStatus

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
    
    def decision_making(self, request: Request, present_services: List[Service]) -> List[List[Tuple[bool, Service]]]:
        """
        This function is called when a request arrives. It must call the decision making algorithm to decide
        which services are going to be assigned to the request. There may be services that are already created, and
        may be used as well (Barges and Trains).
        
        The result of the function is a list of lists. Each internal list represents a REQUEST SERVICE,
        and whenever all request services are fulfilled, the request is considered fulfilled.

        Each REQUEST SERVICE consists of vehicle services, and one can imagine it as a Directed Acyclic Graph.

        This can be represented as a dictionary.
        A scenario corresponding to this DAG would be:
        A train delivers to somewhere (A),
        then 2 trucks can pick up the containers and deliver them to somewhere else (B and C), then a train/barge can pick them up and deliver to final 
        destination.

        This function must wrap the data in a Service object, and return it.
        """

        # class Service(
        #     origin: Any,
        #     destination: Any,
        #     departure_time: Any,
        #     arrival_time: Any,
        #     cost: Any,
        #     capacity: Any,
        #     vehicle_id: Any,
        #     remaining_distance: Any
        # )

        # THIS IS HARDCODED FOR TESTING PURPOSES ONLY, BUT THIS IS HOW THE OUTPUT SHOULD LOOK LIKE
        if request.id == 0:
            return [
                [
                    [True, False, 13, Service(0, 2, 2, 5, 100, 1, 1, 156)], 
                    [False, False, 0, present_services[0]]
                ],
                [
                    [True, False, 13, Service(1, 2, 13, 17, 100, 1, 2, 47)]
                ]
            ]


        