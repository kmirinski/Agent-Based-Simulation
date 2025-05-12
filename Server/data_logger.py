import json
import os
from typing import Dict, List

import numpy as np
from vehicles import Vehicle
from common import Event


FOLDER_NAME = "logs"

EVENT_FILE = "events.json"
ENVIRONMENT_STATES_FILE = "environment_states.json"
VEHICLE_STATES_FILE = "vehicle_states.json"
CALCULATIONS_FILE = "calculations.json"

EVENTS_FILE_PATH = os.path.join(FOLDER_NAME, EVENT_FILE)
ENVIRONMENT_STATES_FILE_PATH = os.path.join(FOLDER_NAME, ENVIRONMENT_STATES_FILE)
VEHICLE_STATES_FILE_PATH = os.path.join(FOLDER_NAME, VEHICLE_STATES_FILE)
CALCULATIONS_FILE_PATH = os.path.join(FOLDER_NAME, CALCULATIONS_FILE)

class EnvironmentStateLogger:
    def __init__(self):
        self.state_dict: Dict[int, Dict[str, np.ndarray]] = {}
        self.vehicle_dict: Dict[int, List[Vehicle]] = {}

    def save_state(self, step: int, state: Dict[str, np.ndarray], vehicles: List[Vehicle]):
        """
        Save the state of the environment at a given step.
        
        Args:
            step (int): The simulation step.
            state (Dict[str, np.ndarray]): The state of the environment.
            vehicles (List[Vehicle]): The list of vehicles in the environment.
        """
        serializable_state = {
            key: value.tolist() if isinstance(value, np.ndarray) else value
            for key, value in state.items()
        }
        self.state_dict[step] = serializable_state
        
        serializable_vehicles = [vehicle.to_dict() for vehicle in vehicles]
        self.vehicle_dict[step] = serializable_vehicles
    
    def log_states(self):
        """
        Log the environment states to a JSON file.
        
        Args:
            state_dict (Dict[int, Dict[str, np.ndarray]]): The state of the environment at each step.
            vehicle_dict (Dict[int, List[Vehicle]]): The list of vehicles in the environment at each step.
        """
        with open(ENVIRONMENT_STATES_FILE_PATH, "w") as file:
            json.dump(self.state_dict, file, indent=4)

        with open(VEHICLE_STATES_FILE_PATH, "w") as file:
            json.dump(self.vehicle_dict, file, indent=4)

class EventLogger:
    def __init__(self):
        self.event_list = np.array([], dtype=Event)

    def save_event(self, event: Event):
        self.event_list = np.append(self.event_list, event)

    def log_events(self):
        """
        Log an event to the JSON file.
        
        Args:
            event (Event): Event to log. Contains timestamp, event type, and vehicle id. 
        """

        event_log_json = json.dumps([event.to_dict() for event in self.event_list], indent=4)

        with open(EVENTS_FILE_PATH, "w") as file:
            file.write(event_log_json)

# class CalculationsLogger:




def create_folder_and_file(folder_name: str, file_name: str, file_path: str, ):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created.")
    else:
        print(f"Folder '{folder_name}' already exists.")

    # Create the file inside the folder
    with open(file_path, "w") as file:
        json.dump([], file, indent=4)
        print(f"File '{file_name}' created in '{file_path}'.")