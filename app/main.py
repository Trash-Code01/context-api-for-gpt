from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import Client, Script
from .database import add_client, get_all_clients, save_script, get_latest_script, log_interaction, delete_client
from .auth import verify_api_key

app = FastAPI(title="The Devacia OS", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CRM ROUTES ---

@app.post("/crm/add-lead", dependencies=[Depends(verify_api_key)])
def create_lead(client: Client):
    return add_client(client)

@app.get("/crm/get-leads", dependencies=[Depends(verify_api_key)])
def read_leads():
    return get_all_clients()

@app.post("/crm/log-activity", dependencies=[Depends(verify_api_key)])
def log_activity(client_name: str, type: str, content: str):
    """
    Log an email, DM, or call. AUTOMATICALLY timestamps it.
    """
    updated_client = log_interaction(client_name, type, content)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Activity Logged", "history": updated_client["history"]}

@app.delete("/crm/delete-lead", dependencies=[Depends(verify_api_key)])
def remove_lead(client_name: str):
    """
    Permanently delete a client to free up space.
    """
    success = delete_client(client_name)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": f"Client {client_name} deleted forever."}

# --- VAULT ROUTES (Unchanged) ---
@app.post("/vault/save-script", dependencies=[Depends(verify_api_key)])
def create_script(script: Script):
    return save_script(script)

@app.get("/vault/get-latest-script", dependencies=[Depends(verify_api_key)])
def read_latest_script():
    script = get_latest_script()
    if not script:
        raise HTTPException(status_code=404, detail="No scripts found")
    return script