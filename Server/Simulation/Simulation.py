import simpy
import pandas as pd
from Agents.Shipper import Shipper
from Agents.LSP import LSP
from Agents.Carrier import Carrier
from Agents.Misc import Request, Event, Event_Type
from queue import PriorityQueue

event_pq = PriorityQueue()
request_dict = {}



def read_data():
    # Read distance matrix
    with open('instance_files/param_dist.csv') as f:
        f.readline().strip().split(',')
        dist_matrix = pd.read_csv(f, header=None).values

    # Read demand
    requests_df = pd.read_csv('instance_files/param_demand_5.csv')

    # Read nodes
    nodes_df = pd.read_csv('instance_files/param_nodes.csv')

    print("Data read successfully")
    
    return dist_matrix, requests_df, nodes_df

def generate_agents(num_shippers, num_lsps, num_carriers):
    shippers = []
    lsps = []
    carriers = []
    
    for i in range(num_carriers):
        carriers.append(Carrier(i))

    for i in range(num_lsps):
        lsps.append(LSP(i))
    
    for i in range(num_shippers):
        shippers.append(Shipper(i))

    print("Agents generated successfully")
    return shippers, lsps, carriers

# Hardcoded assignment of agents to each other
def assign_agents(shippers, lsps, carriers):
    lsps[0].carriers.append(carriers[0])
    lsps[0].carriers.append(carriers[1])
    lsps[1].carriers.append(carriers[2])
    lsps[1].carriers.append(carriers[3])
    shippers[0].lsp_list = lsps
    print("Agents assigned successfully")

def create_requests(shipper, requests_df, dist_matrix):
    print(requests_df)
    for i in range(len(requests_df)):
        
        request_id = requests_df.iloc[i]['id']
        origin = requests_df.iloc[i]['orig']
        destination = requests_df.iloc[i]['dest']
        distance = dist_matrix[origin][destination]
        time_window = [requests_df.iloc[i]['lw'], requests_df.iloc[i]['uw']]
        
        # Subtracting 1 since the request should be processed 1 hour before it has to be dispatched
        request_dict[request_id] = Request(request_id, origin, destination, 
                          requests_df.iloc[i]['amount'], requests_df.iloc[i]['price'], time_window, distance)
        event_pq.put((time_window[0] - 1, Event(time_window[0], Event_Type.DISPATCH, request_id)))
        # event_pq.put((time_window[1], Event(time_window[0], Event_Type.DISPATCH, request_id)))
    print("Requests and events created successfully")


def process_event(env, event, shipper):
    if event.type == Event_Type.DISPATCH:
        print(f"Time {env.now}: Dispatching request {event.request_id}")
        shipper.process_dispatch_request(env, request_dict[event.request_id])
    elif event.type == Event_Type.IN_PROGRESS:
        print(f"Time {env.now}: Delivering request {event.request_id}")
        # shipper.deliver_request(request)
    elif event.type == Event_Type.DELIVERED:
        print(f"Time {env.now}: Delivered request {event.request_id}")
        # shipper.delivered_request(request)
    # elif event.type == Event_Type.NOT_DELIVERED:
    #     shipper.not_delivered_request(env, request_dict[event.request_id])
    else:
        print("Event type not recognized")
        


def event_handler(env, shipper):
    while not event_pq.empty():
        event_time, event = event_pq.get() 
        yield env.timeout(event_time - env.now)  
        process_event(env, event, shipper)


def run_simulation():
    sim_env = simpy.Environment()

    num_shippers = 1
    num_lsps = 2
    num_carriers = 4

    shippers, lsps, carriers = generate_agents(num_shippers, num_lsps, num_carriers)

    # This is done according to the desired scenario to be simulated (will be automized in the future)
    assign_agents(shippers, lsps, carriers)
    dist_matrix, requests_df, nodes_df = read_data()
    create_requests(shippers[0], requests_df, dist_matrix)

    sim_env.process(event_handler(sim_env, shippers[0]))
    sim_env.run()

    print('Simulation finished suceccefully')