from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os

from .models import Client, Script
from .database import add_client, get_all_clients, save_script, get_latest_script, log_interaction, delete_client
from .auth import verify_api_key
from .tools import research_client, create_pdf, send_email_with_attachment

app = FastAPI(title="The Devacia OS", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CRM & VAULT ROUTES (Unchanged) ---
@app.post("/crm/add-lead", dependencies=[Depends(verify_api_key)])
def create_lead(client: Client):
    return add_client(client)

@app.get("/crm/get-leads", dependencies=[Depends(verify_api_key)])
def read_leads():
    return get_all_clients()

@app.post("/crm/log-activity", dependencies=[Depends(verify_api_key)])
def log_activity(client_name: str, type: str, content: str):
    updated_client = log_interaction(client_name, type, content)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Activity Logged", "history": updated_client["history"]}

@app.delete("/crm/delete-lead", dependencies=[Depends(verify_api_key)])
def remove_lead(client_name: str):
    success = delete_client(client_name)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": f"Client {client_name} deleted."}

@app.post("/vault/save-script", dependencies=[Depends(verify_api_key)])
def create_script(script: Script):
    return save_script(script)

@app.get("/vault/get-latest-script", dependencies=[Depends(verify_api_key)])
def read_latest_script():
    script = get_latest_script()
    if not script:
        raise HTTPException(status_code=404, detail="No scripts found")
    return script

# --- NEW SMART AGENT ROUTES ---

@app.post("/agent/research", dependencies=[Depends(verify_api_key)])
def agent_research(client_name: str):
    """
    High-Speed Tavily Research. Returns Data + PDF.
    """
    summary = research_client(client_name)
    # Log research event
    log_interaction(client_name, "System", "Performed AI Research")
    
    filename = f"Report_{client_name.replace(' ', '_')}.pdf"
    pdf_path = create_pdf(filename, f"Dossier: {client_name}", summary)
    
    return {
        "message": "Research Complete", 
        "pdf_file": filename, 
        "summary": summary
    }

@app.post("/agent/create-contract", dependencies=[Depends(verify_api_key)])
def agent_contract(client_name: str, content: str):
    """
    Generates any PDF (Contract, Proposal, etc).
    """
    filename = f"Contract_{client_name.replace(' ', '_')}.pdf"
    pdf_path = create_pdf(filename, f"Contract: {client_name}", content)
    return {"message": "Contract Generated", "pdf_file": filename}

@app.post("/agent/send-email", dependencies=[Depends(verify_api_key)])
def agent_send_email(
    client_email: str, 
    client_name: str, 
    subject: str, 
    body: str, 
    attachment_filename: Optional[str] = None
):
    """
    The UNIVERSAL Emailer.
    - If attachment_filename is provided: Sends PDF.
    - If attachment_filename is empty: Sends Plain Text.
    """
    file_path = None
    
    # Logic: Did the user ask for a file?
    if attachment_filename:
        if os.path.exists(attachment_filename):
            file_path = attachment_filename
        else:
            # If file is missing, warn but send plain email anyway? 
            # Or fail strictly. Let's fail strictly to avoid mistakes.
            raise HTTPException(status_code=404, detail=f"File {attachment_filename} not found. Generate it first.")

    success = send_email_with_attachment(client_email, subject, body, file_path)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email.")
    
    # Log to Memory
    log_type = "Email (Packet)" if file_path else "Email (Plain)"
    log_interaction(client_name, log_type, f"Subject: {subject}")
    
    return {"message": f"Email sent successfully to {client_email}"}