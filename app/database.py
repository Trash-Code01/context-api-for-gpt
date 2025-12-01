import os
import json
from datetime import datetime
from supabase import create_client, Client
from .models import Client, Script

# Initialize Supabase
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

# Graceful fallback if keys are missing (prevents crash, but warns)
if not url or not key:
    print("CRITICAL: SUPABASE KEYS MISSING. Database will fail.")
    supabase = None
else:
    supabase: Client = create_client(url, key)

# --- CLIENT FUNCTIONS ---

def add_client(client: Client):
    if not supabase: return None
    
    # Convert Pydantic model to dict
    data = client.dict(exclude={"id"}) # Let DB handle ID
    
    # Add initial history log
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["history"] = [{
        "date": now,
        "type": "System",
        "content": "Client added to Black Book."
    }]
    
    response = supabase.table("clients").insert(data).execute()
    return response.data[0] if response.data else None

def get_all_clients():
    if not supabase: return []
    response = supabase.table("clients").select("*").execute()
    return response.data

def log_interaction(client_name: str, type: str, content: str):
    if not supabase: return None
    
    # 1. Find the client
    # (Using ILIKE for case-insensitive search)
    response = supabase.table("clients").select("*").ilike("name", f"%{client_name}%").execute()
    
    if not response.data:
        return None
        
    client = response.data[0]
    
    # 2. Append to History
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_event = {"date": now, "type": type, "content": content}
    
    current_history = client.get("history", [])
    if current_history is None: current_history = []
    
    current_history.append(new_event)
    
    # 3. Update DB
    update_response = supabase.table("clients").update({"history": current_history}).eq("id", client["id"]).execute()
    return update_response.data[0]

def delete_client(client_name: str):
    if not supabase: return False
    # Find IDs first to be safe
    response = supabase.table("clients").select("id").ilike("name", f"%{client_name}%").execute()
    if not response.data:
        return False
        
    for record in response.data:
        supabase.table("clients").delete().eq("id", record["id"]).execute()
        
    return True

# --- SCRIPT FUNCTIONS ---

def save_script(script: Script):
    if not supabase: return None
    data = script.dict(exclude={"id"})
    # Convert datetime to string for JSON compatibility if needed
    data["created_at"] = str(data["created_at"])
    
    response = supabase.table("scripts").insert(data).execute()
    return response.data[0]

def get_latest_script():
    if not supabase: return None
    # Order by created_at descending, limit 1
    response = supabase.table("scripts").select("*").order("created_at", desc=True).limit(1).execute()
    return response.data[0] if response.data else None