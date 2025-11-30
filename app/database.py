import json
import os
from typing import List, Optional
from .models import Client, Script

# File where data will be saved
DB_FILE = "devacia_memory.json"

def load_db():
    """Reads the JSON file and returns the data dictionary."""
    if not os.path.exists(DB_FILE):
        return {"clients": [], "scripts": []}
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError):
        return {"clients": [], "scripts": []}

def save_db(data):
    """Writes the data dictionary back to the JSON file."""
    with open(DB_FILE, "w") as f:
        # default=str handles UUIDs and Datetimes automatically
        json.dump(data, f, indent=4, default=str)

# --- CLIENT FUNCTIONS ---

def add_client(client: Client) -> Client:
    data = load_db()
    # Convert Pydantic model to dict
    client_dict = client.dict()
    # Convert UUID/Datetime to string for JSON compatibility
    client_dict["id"] = str(client_dict["id"])
    
    data["clients"].append(client_dict)
    save_db(data)
    return client

def get_all_clients() -> List[dict]:
    data = load_db()
    return data["clients"]

# --- SCRIPT FUNCTIONS ---

def save_script(script: Script) -> Script:
    data = load_db()
    script_dict = script.dict()
    # Convert UUID/Datetime to string
    script_dict["id"] = str(script_dict["id"])
    script_dict["created_at"] = str(script_dict["created_at"])
    
    data["scripts"].append(script_dict)
    save_db(data)
    return script

def get_latest_script() -> Optional[dict]:
    data = load_db()
    if not data["scripts"]:
        return None
    return data["scripts"][-1]