from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

@dataclass
class Node:
    name: str
    longitude: float
    latitude: float

@dataclass
class Link:
    start_longitude: float
    start_latitude: float
    end_longitude: float
    end_latitude: float

@dataclass
class Vehicle:
    """
    A type of vehicle is defined by it's type name (e.g. empty trucks and containers), origin node (ID), destination node (ID), and quantity
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
    A type of vehicle is defined by it's type name (e.g. empty trucks and containers), origin node (ID), destination node (ID), and quantity
    """
    name: str
    origin: int
    destination: int
    quantity: int

class Event_Type(Enum):
    SPAWN_VEHICLE = 0
    DISPATCH_VEHICLE = 1
    DELIVER = 2

class Agent_Type(Enum):
    SHIPPER = 0
    LSP = 1
    CARRIER = 2

@dataclass
class Request:
    id: int
    origin: int                                         # Node ID
    destination: int                                    # Node ID
    volume: float                                       # in m^3
    time_window: Tuple[int, int]                        # Lower and upper bounds
    selected_shipper: int                               # Shipper ID
    distance: int                                       # in km
    weight: float = field(default = 0.0)                # in kg
    penalization_factor: float = field(default= 0.0)    # if the request is not fulfilled within the time window
    full_truckload: bool = field(default = True)        # whether the request can be on the truck with other requests
    is_splittable: bool = field(default = False)        # whether the request can be split into multiple trucks

@dataclass
class Event:
    timestamp: int
    type: Event_Type
    request_id: int
    
    def __lt__(self, other: 'Event'):
        return self.timestamp < other.timestamp
