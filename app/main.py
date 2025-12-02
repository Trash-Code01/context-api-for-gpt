from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os

from .models import Client, Script
from .database import add_client, get_all_clients, save_script, get_latest_script, log_interaction, delete_client
from .auth import verify_api_key
from .tools import research_client, create_pdf, send_email_with_attachment, send_sms_message, send_whatsapp_message

app = FastAPI(title="Naomi AI - Devacia OS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PREMIUM RESPONSE HELPERS ---
def success_response(action: str, details: dict = None):
    """Returns clean, user-friendly success messages"""
    response = {"status": "success", "action": action}
    if details:
        response.update(details)
    return response

def error_response(message: str):
    """Returns clean, user-friendly error messages"""
    return {"status": "error", "message": message}

# --- CRM ROUTES (MEMORY) ---
@app.post("/crm/add-lead", dependencies=[Depends(verify_api_key)])
def create_lead(client: Client):
    """Add a new client to the pipeline"""
    result = add_client(client)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to add client")
    
    return success_response(
        action="client_added",
        details={
            "client_name": result.get("name"),
            "company": result.get("company"),
            "status": result.get("status", "Lead")
        }
    )

@app.get("/crm/get-leads", dependencies=[Depends(verify_api_key)])
def read_leads():
    """Get all clients in the pipeline"""
    clients = get_all_clients()
    
    # Organize by status for premium display
    vip = [c for c in clients if c.get("status") == "VIP"]
    active = [c for c in clients if c.get("status") == "Lead"]
    cold = [c for c in clients if c.get("status") == "Cold"]
    
    return success_response(
        action="pipeline_retrieved",
        details={
            "total": len(clients),
            "vip_count": len(vip),
            "active_count": len(active),
            "cold_count": len(cold),
            "clients": clients
        }
    )

@app.post("/crm/log-activity", dependencies=[Depends(verify_api_key)])
def log_activity(client_name: str, type: str, content: str):
    """Log an interaction with a client"""
    updated = log_interaction(client_name, type, content)
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return success_response(
        action="activity_logged",
        details={
            "client_name": client_name,
            "interaction_type": type
        }
    )

@app.delete("/crm/delete-lead", dependencies=[Depends(verify_api_key)])
def remove_lead(client_name: str):
    """Remove a client from the pipeline"""
    if not delete_client(client_name):
        raise HTTPException(status_code=404, detail="Client not found")
    
    return success_response(
        action="client_deleted",
        details={"client_name": client_name}
    )

# --- AGENT ROUTES (TOOLS) ---
@app.post("/agent/research", dependencies=[Depends(verify_api_key)])
def agent_research(client_name: str):
    """Research a prospect using AI"""
    summary = research_client(client_name)
    
    if "Error:" in summary or "Failed:" in summary:
        raise HTTPException(status_code=500, detail="Research failed")
    
    log_interaction(client_name, "System", "AI Research Completed")
    filename = f"Report_{client_name.replace(' ', '_')}.pdf"
    create_pdf(filename, f"Research: {client_name}", summary)
    
    return success_response(
        action="research_completed",
        details={
            "client_name": client_name,
            "summary": summary,
            "pdf_generated": filename
        }
    )

@app.post("/agent/create-contract", dependencies=[Depends(verify_api_key)])
def agent_contract(client_name: str, content: str):
    """Generate a contract PDF"""
    filename = f"Contract_{client_name.replace(' ', '_')}.pdf"
    create_pdf(filename, f"Contract: {client_name}", content)
    
    return success_response(
        action="contract_generated",
        details={
            "client_name": client_name,
            "filename": filename
        }
    )

@app.post("/agent/send-email", dependencies=[Depends(verify_api_key)])
def agent_email(client_email: str, client_name: str, subject: str, body: str, attachment_filename: Optional[str] = None):
    """Send email with optional attachment"""
    file_path = attachment_filename if (attachment_filename and os.path.exists(attachment_filename)) else None
    
    if not send_email_with_attachment(client_email, subject, body, file_path):
        raise HTTPException(status_code=500, detail="Email delivery failed")
    
    log_interaction(client_name, "Email", f"Subject: {subject}")
    
    return success_response(
        action="email_sent",
        details={
            "recipient": client_email,
            "client_name": client_name,
            "subject": subject,
            "has_attachment": file_path is not None
        }
    )

@app.post("/agent/send-sms", dependencies=[Depends(verify_api_key)])
def agent_sms(client_phone: str, client_name: str, message: str):
    """Send SMS message"""
    if not send_sms_message(client_phone, message):
        raise HTTPException(status_code=500, detail="SMS delivery failed")
    
    log_interaction(client_name, "SMS", f"Message sent")
    
    return success_response(
        action="sms_sent",
        details={
            "recipient": client_phone,
            "client_name": client_name
        }
    )

@app.post("/agent/send-whatsapp", dependencies=[Depends(verify_api_key)])
def agent_whatsapp(client_phone: str, client_name: str, message: str):
    """Send WhatsApp message"""
    if not send_whatsapp_message(client_phone, message):
        raise HTTPException(status_code=500, detail="WhatsApp delivery failed")
    
    log_interaction(client_name, "WhatsApp", f"Message sent")
    
    return success_response(
        action="whatsapp_sent",
        details={
            "recipient": client_phone,
            "client_name": client_name
        }
    )

# --- VAULT ROUTES ---
@app.post("/vault/save-script", dependencies=[Depends(verify_api_key)])
def create_script(script: Script):
    """Save a script to the vault"""
    result = save_script(script)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to save script")
    
    return success_response(
        action="script_saved",
        details={
            "title": script.title,
            "client_name": script.client_name
        }
    )

@app.get("/vault/get-latest-script", dependencies=[Depends(verify_api_key)])
def read_script():
    """Get the most recent script"""
    script = get_latest_script()
    if not script:
        raise HTTPException(status_code=404, detail="No scripts found")
    
    return success_response(
        action="script_retrieved",
        details=script
    )