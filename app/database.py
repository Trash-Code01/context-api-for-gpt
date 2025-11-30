from typing import List, Optional
from .models import Client, Script

# In-memory databases
clients: List[Client] = []
scripts: List[Script] = []

def add_client(client: Client) -> Client:
    clients.append(client)
    return client

def get_all_clients() -> List[Client]:
    return clients

def save_script(script: Script) -> Script:
    scripts.append(script)
    return script

def get_latest_script() -> Optional[Script]:
    if not scripts:
        return None
    # Assuming the latest one is the last one added
    return scripts[-1]
