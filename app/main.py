from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os

from .models import Client, Script
from .database import add_client, get_all_clients, save_script, get_latest_script, log_interaction, delete_client
from .auth import verify_api_key
from .tools import research_client, create_pdf, send_email_with_attachment, send_sms_message, send_whatsapp_message

app = FastAPI(title="The Devacia OS", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CRM ROUTES (MEMORY) ---
@app.post("/crm/add-lead", dependencies=[Depends(verify_api_key)])
def create_lead(client: Client):
    return add_client(client)

@app.get("/crm/get-leads", dependencies=[Depends(verify_api_key)])
def read_leads():
    return get_all_clients()

@app.post("/crm/log-activity", dependencies=[Depends(verify_api_key)])
def log_activity(client_name: str, type: str, content: str):
    updated = log_interaction(client_name, type, content)
    if not updated: raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Logged", "history": updated["history"]}

@app.delete("/crm/delete-lead", dependencies=[Depends(verify_api_key)])
def remove_lead(client_name: str):
    if delete_client(client_name): return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Client not found")

# --- AGENT ROUTES (TOOLS) ---
@app.post("/agent/research", dependencies=[Depends(verify_api_key)])
def agent_research(client_name: str):
    summary = research_client(client_name)
    log_interaction(client_name, "System", "AI Research Completed")
    filename = f"Report_{client_name.replace(' ', '_')}.pdf"
    create_pdf(filename, f"Dossier: {client_name}", summary)
    return {"message": "Research Done", "summary": summary, "pdf_file": filename}

@app.post("/agent/create-contract", dependencies=[Depends(verify_api_key)])
def agent_contract(client_name: str, content: str):
    filename = f"Contract_{client_name.replace(' ', '_')}.pdf"
    create_pdf(filename, f"Contract: {client_name}", content)
    return {"message": "Contract Generated", "pdf_file": filename}

@app.post("/agent/send-email", dependencies=[Depends(verify_api_key)])
def agent_email(client_email: str, client_name: str, subject: str, body: str, attachment_filename: Optional[str] = None):
    file_path = attachment_filename if (attachment_filename and os.path.exists(attachment_filename)) else None
    if not send_email_with_attachment(client_email, subject, body, file_path):
        raise HTTPException(status_code=500, detail="Email Failed")
    log_interaction(client_name, "Email Sent", f"Subject: {subject}")
    return {"message": "Email Sent"}

@app.post("/agent/send-sms", dependencies=[Depends(verify_api_key)])
def agent_sms(client_phone: str, client_name: str, message: str):
    if not send_sms_message(client_phone, message):
        raise HTTPException(status_code=500, detail="SMS Failed")
    log_interaction(client_name, "SMS Sent", f"Msg: {message}")
    return {"message": "SMS Sent"}

@app.post("/agent/send-whatsapp", dependencies=[Depends(verify_api_key)])
def agent_whatsapp(client_phone: str, client_name: str, message: str):
    if not send_whatsapp_message(client_phone, message):
        raise HTTPException(status_code=500, detail="WhatsApp Failed")
    log_interaction(client_name, "WhatsApp Sent", f"Msg: {message}")
    return {"message": "WhatsApp Sent"}

# --- VAULT ROUTES ---
@app.post("/vault/save-script", dependencies=[Depends(verify_api_key)])
def create_script(script: Script):
    return save_script(script)

@app.get("/vault/get-latest-script", dependencies=[Depends(verify_api_key)])
def read_script():
    return get_latest_script() or HTTPException(status_code=404, detail="No scripts")