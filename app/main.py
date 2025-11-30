from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import Client, Script
from .database import add_client, get_all_clients, save_script, get_latest_script
from .auth import verify_api_key

app = FastAPI(title="The Devacia OS")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CRM ROUTES
@app.post("/crm/add-lead", dependencies=[Depends(verify_api_key)], response_model=Client, tags=["CRM"])
def create_lead(client: Client):
    """
    Add a new lead to the CRM.
    Requires x-api-key header.
    """
    return add_client(client)

@app.get("/crm/get-leads", dependencies=[Depends(verify_api_key)], response_model=List[Client], tags=["CRM"])
def read_leads():
    """
    Get all leads from the CRM.
    Requires x-api-key header.
    """
    return get_all_clients()

# VAULT ROUTES
@app.post("/vault/save-script", dependencies=[Depends(verify_api_key)], response_model=Script, tags=["Vault"])
def create_script(script: Script):
    """
    Save a generated script to the Vault.
    Requires x-api-key header.
    """
    return save_script(script)

@app.get("/vault/get-latest-script", dependencies=[Depends(verify_api_key)], response_model=Script, tags=["Vault"])
def read_latest_script():
    """
    Get the most recently saved script from the Vault.
    Requires x-api-key header.
    """
    script = get_latest_script()
    if not script:
        raise HTTPException(status_code=404, detail="No scripts found")
    return script
