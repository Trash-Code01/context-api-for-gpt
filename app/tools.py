import os
import base64
import requests
from fpdf import FPDF
from tavily import TavilyClient
from twilio.rest import Client as TwilioClient

# --- 1. RESEARCH TOOL (TAVILY) ---
def research_client(name: str) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key: return "Error: Tavily Key missing."
    try:
        tavily = TavilyClient(api_key=api_key)
        response = tavily.search(query=f"{name} profession brand CEO details", search_depth="advanced")
        summary = f"RESEARCH DOSSIER: {name}\n\n"
        results = response.get('results', [])[:3]
        if not results: return f"No data found for {name}."
        for i, r in enumerate(results, 1):
            summary += f"SOURCE {i}: {r.get('title')}\nURL: {r.get('url')}\nINTEL: {r.get('content')[:400]}...\n\n"
        return summary
    except Exception as e:
        return f"Research Failed: {str(e)}"

# --- 2. PDF TOOL ---
def create_pdf(filename: str, title: str, content: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    # Fix encoding for compatibility
    content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, content)
    if not filename.endswith(".pdf"): filename += ".pdf"
    pdf.output(filename)
    return os.path.abspath(filename)

# --- 3. EMAIL TOOL (BREVO API - BYPASSES BLOCKS) ---
def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_path: str = None) -> bool:
    BREVO_KEY = os.getenv("BREVO_KEY")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    
    if not BREVO_KEY or not SENDER_EMAIL:
        print("Error: Brevo Credentials missing.")
        return False

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_KEY,
        "content-type": "application/json"
    }
    
    payload = {
        "sender": {"name": "The Devacia Team", "email": SENDER_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body
    }

    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                payload["attachment"] = [{"content": encoded, "name": os.path.basename(attachment_path)}]
        except Exception as e: 
            print(f"Attachment Error: {e}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        # Brevo returns 201 for success
        if response.status_code in [200, 201, 202]:
            return True
        else:
            print(f"Brevo Error: {response.text}")
            return False
    except Exception as e:
        print(f"Email Request Failed: {e}")
        return False

# --- 4. SMS TOOL (TWILIO) ---
def send_sms_message(to_number: str, message_body: str) -> bool:
    SID = os.getenv("TWILIO_SID")
    TOKEN = os.getenv("TWILIO_TOKEN")
    FROM = os.getenv("TWILIO_FROM_NUMBER")
    
    if not SID or not TOKEN or not FROM: 
        print("Error: Twilio SMS Credentials missing.")
        return False
    try:
        client = TwilioClient(SID, TOKEN)
        client.messages.create(body=message_body, from_=FROM, to=to_number)
        return True
    except Exception as e:
        print(f"SMS Error: {e}")
        return False

# --- 5. WHATSAPP TOOL (TWILIO) ---
def send_whatsapp_message(to_number: str, message_body: str) -> bool:
    SID = os.getenv("TWILIO_SID")
    TOKEN = os.getenv("TWILIO_TOKEN")
    # This must match the variable in Render EXACTLY
    FROM = os.getenv("TWILIO_WHATSAPP_FROM") 
    
    if not SID or not TOKEN or not FROM: 
        print("Error: Twilio WhatsApp Credentials missing.")
        return False
    try:
        client = TwilioClient(SID, TOKEN)
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
            
        client.messages.create(body=message_body, from_=FROM, to=to_number)
        return True
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return False