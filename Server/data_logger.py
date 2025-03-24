import json
import os

import numpy as np
from common import Event


FOLDER_NAME = "logs"
EVENT_FILE = "events.json"
EVENTS_FILE_PATH = os.path.join(FOLDER_NAME, EVENT_FILE)


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