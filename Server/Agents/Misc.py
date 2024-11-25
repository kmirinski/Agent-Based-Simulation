import random
import math
from Simulation.Global import *

from enum import Enum


class Request:
    def __init__(self, id, origin, destination, amount, price, time_window, distance):
        self.id = id
        self.origin = origin
        self.destination = destination
        self.amount = amount
        self.price = price
        self.time_window = time_window
        self.distance = distance

class Truck:
    def __init__(self, carrier, request_id, distance, average_speed=60):
        self.carrier = carrier
        self.request_id = request_id
        self.distance = distance
        self.average_speed = average_speed + random.uniform(-10, 10)
        self.travel_time = math.ceil(self.distance / self.average_speed)

    def estimate_time(self, env):
        print(f"Distance: {self.distance}, Average Speed: {self.average_speed}, Travel Time: {self.travel_time}")
        enqueue_event(env.now + self.travel_time + 1, Event(env.now + self.travel_time, Event_Type.DELIVERED, self.request_id))
        return self.travel_time


class Event_Type(Enum):
    DISPATCHED = 1
    # IN_PROGRESS = 2
    DELIVERED = 3
    # NOT_DELIVERED = 4

# class Event_Type(Enum):
#     NOT_ARRIVED = 0
#     ARRIVED = 1
#     DISPATCHED = 2
#     # IN_PROGRESS = 2
#     DELIVERED = 3
#     # NOT_DELIVERED = 4

class Event:
    def __init__(self, timestamp, type, request_id):
        self.timestamp = timestamp
        self.type = type
        self.request_id = request_id

    # This function set the priority of the events
    def __lt__(self, other):
        if self.timestamp == other.timestamp:
            return self.type.value < other.type.value  # Tie-breaking logic
        return self.timestamp < other.timestamp