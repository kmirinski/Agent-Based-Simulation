from dataclasses import dataclass
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

class Event_Type(Enum):
    SPAWN_VEHICLE = 0
    DISPATCH_VEHICLE = 1
    DELIVER = 2

@dataclass
class Request:
    id: int
    origin: int                     # Node ID
    destination: int                # Node ID
    amount: int
    price: int
    time_window: Tuple[int, int]    # Lower and upper bounds
    selected_shipper: int
    distance: int

@dataclass
class Event:
    timestamp: int
    type: Event_Type
    request_id: int
    
    def __lt__(self, other: 'Event'):
        return self.timestamp < other.timestamp
