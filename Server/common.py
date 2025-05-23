from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, TypeAlias

AccessType: TypeAlias = Tuple[bool, bool, bool]


@dataclass
class Node:
    """
    A terminal is defined by its name, longitude, latitude, and accessibility.
    The accessibility is a tuple of three booleans, indicating if the terminal is accessible by truck, train, or barge.
    The first element of the tuple corresponds to truck accessibility, the second to train accessibility, 
    and the third to barge accessibility.
    
    Example 1: (True, False, True) indicates that the terminal is accessible by truck and barge, but not by train.
    Example 2: (True, True, True) indicates that the terminal is accessible by all the types of vehicles.
    """
    name: str
    longitude: float
    latitude: float
    accessibility: AccessType = (True, True, True) 

@dataclass
class Link:
    start_longitude: float
    start_latitude: float
    end_longitude: float
    end_latitude: float

@dataclass
class Vehicle:
    """
    A type of vehicle is defined by it's type name (e.g. empty trucks and containers), 
    origin node (ID), destination node (ID), and quantity.
    """
    name: str
    origin: int
    destination: int
    quantity: int
    distance: int
    remaining_distance: int
    speed: int

@dataclass
class NetworkVehicle:
    """
    A type of vehicle is defined by it's type name (e.g. empty trucks and containers), 
    origin node (ID), destination node (ID), and quantity.
    """
    name: str
    origin: int
    destination: int
    quantity: int

class Event_Type(Enum):
    REQUEST_ARRIVED = 0
    REQUEST_COMPLETED = 1

    TRUCK_DEPARTED = 2
    TRAIN_DEPARTED = 3
    BARGE_DEPARTED = 4

    TRUCK_ARRIVED = 5
    TRAIN_ARRIVED = 6
    BARGE_ARRIVED = 7

    TRAIN_LOADING = 8
    BARGE_LOADING = 9

class Agent_Type(Enum):
    SHIPPER = 0
    LSP = 1
    CARRIER = 2

@dataclass
class Request:
    id: int
    origin: int                                         # Node ID
    destination: int                                    # Node ID
    amount: int                                         # in euro pallets
    time_window: Tuple[int, int]                        # Lower and upper bounds
    selected_shipper: int                               # Shipper ID
    distance: int                                       # in km

    services: List[int]                                 # Number of services associated with the request

    def is_request_fulfilled(self):
        return sum(self.services) == 0



    # penalization_factor: float = field(default= 0.0)    # if the request is not fulfilled within the time window
    # full_truckload: bool = field(default = True)        # whether the request can be on the truck with other requests
    # is_splittable: bool = field(default = False)        # whether the request can be split into multiple trucks



@dataclass
class Event:
    timestamp: int
    type: Event_Type
    request_id: int = -1
    vehicle_id: int = -1
    request_service_id: int = -1
    
    def __lt__(self, other: 'Event'):
        return self.timestamp < other.timestamp
    
    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "type": self.type.name
        }

