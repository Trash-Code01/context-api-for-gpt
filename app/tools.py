import requests
from bs4 import BeautifulSoup
from googlesearch import search
from fpdf import FPDF
import base64
import os

# --- 1. RESEARCH TOOL ---
def research_client(name: str) -> str:
    """Googles the client name, finds top 3 links, and scrapes the first one."""
    try:
        # Search Google
        results = list(search(name, num_results=3, advanced=True))
        if not results:
            return f"No Google results found for {name}."

        summary = f"Research for {name}:\n\nTop Links:\n"
        for r in results:
            summary += f"- {r.title}: {r.url}\n"

        # Scrape First Link
        first_url = results[0].url
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            page = requests.get(first_url, headers=headers, timeout=5)
            soup = BeautifulSoup(page.content, "html.parser")
            
            title = soup.title.string if soup.title else "No Title"
            text = soup.get_text(separator=" ", strip=True)[:500]
            
            summary += f"\n--- SCRAPED DATA ({first_url}) ---\n"
            summary += f"Title: {title}\n"
            summary += f"Snippet: {text}...\n"
        except Exception as e:
            summary += f"\n[Scraping Failed: {e}]"

        return summary
    except Exception as e:
        return f"Research failed: {e}"

# --- 2. PDF TOOL ---
def create_pdf(filename: str, title: str, content: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    
    # Fix encoding issues
    content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, content)
    
    if not filename.endswith(".pdf"):
        filename += ".pdf"
    
    pdf.output(filename)
    return os.path.abspath(filename)

# --- 3. EMAIL TOOL (BREVO API) ---
def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_path: str = None) -> bool:
    BREVO_KEY = os.getenv("BREVO_KEY")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")

    if not BREVO_KEY or not SENDER_EMAIL:
        print("Error: Brevo credentials missing.")
        return False

    url = "https://api.brevo.com/v3/smtp/email"
    
    headers = {
        "accept": "application/json",
        "api-key": BREVO_KEY,
        "content-type": "application/json"
    }

    payload = {
        "sender": {"email": SENDER_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body
    }

    # Handle Attachment
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            # Encode file to Base64 for the API
            encoded_content = base64.b64encode(f.read()).decode("utf-8")
            filename = os.path.basename(attachment_path)
            
            payload["attachment"] = [
                {
                    "content": encoded_content,
                    "name": filename
                }
            ]

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