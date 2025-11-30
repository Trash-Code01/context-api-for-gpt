import json
import os
from datetime import datetime
from typing import List, Optional
from .models import Client, Script, Interaction

DB_FILE = "devacia_memory.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"clients": [], "scripts": []}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"clients": [], "scripts": []}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4, default=str)

# --- CLIENT LOGIC ---

def add_client(client: Client) -> Client:
    data = load_db()
    client_dict = client.dict()
    client_dict["id"] = str(client_dict["id"])
    
    # Auto-Log the creation date
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_dict["history"].append({
        "date": now,
        "type": "System",
        "content": "Client added to Black Book."
    })
    
    data["clients"].append(client_dict)
    save_db(data)
    return client

def get_all_clients() -> List[dict]:
    data = load_db()
    return data["clients"]

def log_interaction(client_name: str, type: str, content: str):
    """Finds a client and adds a timestamped note."""
    data = load_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # THE CLOCK
    
    for client in data["clients"]:
        if client_name.lower() in client["name"].lower():
            new_event = {
                "date": now,
                "type": type,
                "content": content
            }
            client["history"].append(new_event)
            save_db(data)
            return client
    return None

def delete_client(client_name: str):
    """Removes a client permanently."""
    data = load_db()
    original_count = len(data["clients"])
    # Filter out the client matching the name
    data["clients"] = [c for c in data["clients"] if client_name.lower() not in c["name"].lower()]
    
    if len(data["clients"]) < original_count:
        save_db(data)
        return True
    return False

# --- SCRIPT LOGIC (Unchanged) ---
def save_script(script: Script):
    data = load_db()
    s_dict = script.dict()
    s_dict["id"], s_dict["created_at"] = str(s_dict["id"]), str(s_dict["created_at"])
    data["scripts"].append(s_dict)
    save_db(data)
    return script

def get_latest_script():
    data = load_db()
    return data["scripts"][-1] if data["scripts"] else None