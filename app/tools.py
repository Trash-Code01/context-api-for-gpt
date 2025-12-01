import os
import base64
import requests
from fpdf import FPDF
from tavily import TavilyClient

# --- 1. RESEARCH TOOL (TAVILY API) ---
def research_client(name: str) -> str:
    """
    Uses Tavily AI Search to get instant, structured data.
    Speed: < 2 seconds. No blocking.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: Tavily API Key missing in Render."

    try:
        tavily = TavilyClient(api_key=api_key)
        # Advanced search to get details without visiting every site manually
        response = tavily.search(query=f"{name} profession brand CEO social media details", search_depth="advanced")
        
        summary = f"RESEARCH DOSSIER: {name}\n\n"
        
        # Parse the top 3 AI-curated results
        results = response.get('results', [])[:3]
        if not results:
            return f"No AI data found for {name}."

        for i, result in enumerate(results, 1):
            title = result.get('title', 'No Title')
            url = result.get('url', 'No URL')
            content = result.get('content', 'No Content')[:500] # Grab substantial context
            
            summary += f"SOURCE {i}: {title}\n"
            summary += f"URL: {url}\n"
            summary += f"INTEL: {content}...\n\n"
            
        return summary

    except Exception as e:
        return f"Tavily Search Failed: {str(e)}"

# --- 2. PDF TOOL ---
def create_pdf(filename: str, title: str, content: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    
    # Fix encoding for emojis/symbols that break PDFs
    content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, content)
    
    if not filename.endswith(".pdf"):
        filename += ".pdf"
    
    pdf.output(filename)
    return os.path.abspath(filename)

# --- 3. EMAIL TOOL (SMART SENDER) ---
def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_path: str = None) -> bool:
    """
    Sends email via Brevo API. 
    Handles BOTH plain text and attachments automatically.
    """
    BREVO_KEY = os.getenv("BREVO_KEY")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")

    if not BREVO_KEY or not SENDER_EMAIL:
        print("Error: Credentials missing.")
        return False

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_KEY,
        "content-type": "application/json"
    }

    # Professional Sender Name
    payload = {
        "sender": {"name": "The Devacia Team", "email": SENDER_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body
    }

    # If attachment exists, add it. If not, send plain text.
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, "rb") as f:
                encoded_content = base64.b64encode(f.read()).decode("utf-8")
                filename = os.path.basename(attachment_path)
                payload["attachment"] = [{"content": encoded_content, "name": filename}]
        except Exception as e:
            print(f"Attachment Error: {e}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201, 202]:
            return True
        else:
            print(f"Brevo Error: {response.text}")
            return False
    except Exception as e:
        print(f"API Request Failed: {e}")
        return False