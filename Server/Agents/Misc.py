import random
import math
import Simulation

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
        self.travel_time = distance / self.average_speed

    def estimate_time(self):
        travel_time = math.ceil(self.distance / self.average_speed)
        Simulation.event_pq.put((Simulation.env.now + travel_time, Event(Event_Type.DELIVERED, self.request_id)))
    


class Event_Type(Enum):
    DISPATCH = 1
    # IN_PROGRESS = 2
    DELIVERED = 3
    # NOT_DELIVERED = 4

class Event:
    def __init__(self, timestamp, type, request_id):
        self.timestamp = timestamp
        self.type = type
        self.request_id = request_id