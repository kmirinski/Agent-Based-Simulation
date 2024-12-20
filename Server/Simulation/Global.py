from queue import PriorityQueue

event_pq = PriorityQueue()
request_dict = {}

shippers = []
lsps = []
carriers = []


# Event Priority Queue Abstraction
def enqueue_event(priority, event):
    event_pq.put((priority, event))

def print_all_ids():
    for (i, event) in event_pq.queue:
        print(f'Event priority: {i}, Event timestamp: {event.timestamp}')

def pq_queue_is_empty():
    return event_pq.empty()

def get_event():
    return event_pq.get()

def peek_event():
    return event_pq.queue[0]


# Request Abstaction Functions
def add_request(key, value):
    request_dict[key] = value

def get_request(key):
    return request_dict[key]


# class AgentContainer:
#     def __init__(self):
#         self.shippers = {}
#         self.lsps = {}
#         self.carriers = {}

#     def add_shipper(self, shipper):
#         self.shippers[shipper.id] = shipper

#     def add_lsp(self, lsp):
#         self.lsps[lsp.id] = lsp

#     def add_carrier(self, carrier):
#         self.carriers[carrier.id] = carrier

#     def get_shipper(self, id):
#         return self.shippers[id]
    
#     def get_lsp(self, id):
#         return self.lsps[id]
    
#     def get_carrier(self, id):
#         return self.carriers[id]
    
# agents_container = AgentContainer()
    



    

    
        
