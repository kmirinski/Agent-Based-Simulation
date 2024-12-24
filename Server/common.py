from dataclasses import dataclass

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