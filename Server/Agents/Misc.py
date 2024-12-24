import random
import math
from typing import Tuple

from dataclasses import dataclass
from enum import Enum

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


class Truck:
    def __init__(self, carrier, request_id, distance, average_speed=60):
        self.carrier = carrier
        self.request_id = request_id
        self.distance = distance
        self.average_speed = average_speed + random.uniform(-10, 10)
        self.travel_time = math.ceil(self.distance / self.average_speed)

    def estimate_time(self, env):
        print(f"Distance: {self.distance}, Average Speed: {self.average_speed}, Travel Time: {self.travel_time}")
        enqueue_event(env.now + self.travel_time + 1, Event(env.now + self.travel_time + 1, Event_Type.DELIVERED, self.request_id))
        return self.travel_time
