# Agent-Based Simulation Backend Application

## Overview
This software runs logistics simulations based on input files, and saves each intermediate state of the environment in a JSON format, that can be used for visualizing. The three main agents are Shipper, Carrier and Logistic Service Provider (LSP). The shippers initate the incoming requests (demand), and the carriers own a fleed of vehicles that are responsible for executing the requests (supply). The LSPs are intermediate between those two. The model can handle requests that are processed by multiple vehicles (including passing containers to each other at some intermediate stop).

### Setting Up the Project

To get started with the project, follow these steps:

1. **Create and activate a virtual environment** (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

2. **Install the required dependencies**:

   Make sure you're in the root directory of the project (where `requirements.txt` is located), then run:

   ```bash
   pip install -r requirements.txt
   ```

   This will install all the necessary packages listed in the `requirements.txt` file.

## Input
The user is required to have the following files and their corresponding format:
- **List of Requests** - This file should be a CSV containing all shipment requests in the simulation. Each row represents one request with the following columns:

| Column     | Description                                                                 |
|------------|-----------------------------------------------------------------------------|
| `id`       | Unique identifier for the request                                           |
| `orig`     | ID of the origin node                                                       |
| `dest`     | ID of the destination node                                                  |
| `amount`   | Number of units to be transported (in euro pallets)                                        |
| `price`    | Used by the provided files, but does not matter                                 |
| `lw`       | The exact time of arrival |
| `uw`       | Upper bound of the time window in which the request must be fulfilled (inclusive) |
| `selected` | ID of the shipper |


- **List of Nodes** - This file should be a CSV containing all the nodes (locations) used in the simulation, such as origins, destinations, and facilities. Each row represents one node with the following columns:

| Column     | Description                                                     |
|------------|-----------------------------------------------------------------|
| `id`       | Unique identifier for the node                                  |
| `type`     | Used in the provided files, but does not matter |
| `name`     | Short name or code for the node (used for quick reference)      |
| `long_name`| Full descriptive name of the node (e.g., a city or facility name) |


- **List of Services** - This file should be a CSV containing all the service routes for trains and barges known in advance. Each row represents a single service with the following columns:

| Column          | Description                                                      |
|-----------------|------------------------------------------------------------------|
| `origin`        | ID of the origin node (the starting point of the service route)  |
| `destination`   | ID of the destination node (the end point of the service route)  |
| `departure_time`| The time when the service departs from the origin node           |
| `arrival_time`  | The time when the service arrives at the destination node        |
| `cost`          | The cost associated with using this service                      |
| `capacity`      | The capacity of the service (e.g., number of containers it can carry) |
| `vehicle_id`    | ID of the vehicle assigned to this service (reference to vehicles list) |


- **List of Vehicles** - This file should be a CSV containing all the vehicles used in the simulation. Each row represents a single vehicle with the following columns:

| Column          | Description                                                      |
|-----------------|------------------------------------------------------------------|
| `id`            | Unique identifier for the vehicle                                |
| `name`          | Name or type of the vehicle (e.g., "Truck", "Train", etc.)       |
| `initial_location`| ID of the node where the vehicle is initially located           |
| `max_containers`| Maximum number of containers or units the vehicle can carry      |
| `unit_cost`     | The cost per unit of service provided by the vehicle             |
| `emission_factor`| The emission factor associated with the vehicle (e.g., CO2 emissions per unit transported) |
| `carrier_id`    | ID of the carrier that owns the vehicle (if applicable)          |


- **Distance Matrix** - 
This file should be a CSV containing the distances between nodes. The matrix is square, with the number of rows and columns equal to the number of nodes. Each entry represents the distance or time from one node to another.

**Example:**

```csv
3,3
0,210,156
210,0,47
156,47,0
```

## Future Work
 - A decision-making must be adapted to this system. In `Server/agents.py` (called by the shipper) the format of the output of the algorithm is specified. It is important to mention that this program operates under the assumption that all the constraints (e.g., after running it for an arrived request, it should guarantee that the amount for a specific service is not exceeded).

 - The program should take into account the costs and emissions of the requests. In its current state it just processes the requests without any constraints.

 - Expand the functionality of trucks - a starting point would be to implement long-haul/local trucks, or introduce the option of truck processing more than 1 request simultaneously. 

 - The code can be refactored and optimized further. Due to timing constraints, this was not feasible.

 - Automated logic for parsing agent files - details about shippers, carriers and LSPs.