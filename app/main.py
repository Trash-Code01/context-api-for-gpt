from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import Client, Script
from .database import add_client, get_all_clients, save_script, get_latest_script, log_interaction, delete_client
from .auth import verify_api_key
from .tools import research_client, create_pdf, send_email_with_attachment
import os

app = FastAPI(title="The Devacia OS", version="3.0.0")

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

# --- VAULT ROUTES ---
@app.post("/vault/save-script", dependencies=[Depends(verify_api_key)])
def create_script(script: Script):
    return save_script(script)

@app.get("/vault/get-latest-script", dependencies=[Depends(verify_api_key)])
def read_latest_script():
    script = get_latest_script()
    if not script:
        raise HTTPException(status_code=404, detail="No scripts found")
    return script

# --- AGENT ROUTES ---

@app.post("/agent/research", dependencies=[Depends(verify_api_key)])
def agent_research(client_name: str):
    """
    Research a client and generate a dossier PDF.
    """
    summary = research_client(client_name)
    pdf_path = create_pdf(f"Dossier_{client_name}", f"Research Dossier: {client_name}", summary)
    return {"message": "Research done", "summary": summary, "pdf": pdf_path}

@app.post("/agent/create-contract", dependencies=[Depends(verify_api_key)])
def agent_contract(client_name: str, service_name: str, price: str):
    """
    Generate a contract PDF.
    """
    content = f"AGREEMENT\n\nThis contract is between Devacia Agency and {client_name}.\n\nService: {service_name}\nPrice: {price}\n\nSigned: ____________________"
    pdf_path = create_pdf(f"Contract_{client_name}", f"Contract for {client_name}", content)
    return {"message": "Contract generated. Ready to send.", "pdf": pdf_path}

@app.post("/agent/send-packet", dependencies=[Depends(verify_api_key)])
def agent_send(client_email: str, client_name: str, doc_type: str):
    """
    Send an email with the attached PDF (contract or report).
    """
    if doc_type.lower() == "contract":
        filename = f"Contract_{client_name}.pdf"
        subject = f"Contract for {client_name}"
        body = "Please find the attached contract."
    elif doc_type.lower() == "report":
        filename = f"Dossier_{client_name}.pdf"
        subject = f"Research Report for {client_name}"
        body = "Here is the research report."
    else:
        raise HTTPException(status_code=400, detail="Invalid doc_type. Use 'contract' or 'report'.")

    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail=f"File {filename} not found. Generate it first.")

    success = send_email_with_attachment(client_email, subject, body, filename)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email. Check server logs.")
    
    return {"message": "Email sent."}