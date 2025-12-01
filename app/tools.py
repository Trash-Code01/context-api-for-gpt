import requests
from bs4 import BeautifulSoup
from googlesearch import search
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# --- RESEARCH TOOL ---
def research_client(name: str) -> str:
    """Googles the client name, finds top 3 links, and scrapes the first one."""
    try:
        results = list(search(name, num_results=3, advanced=True))
        if not results:
            return f"No Google results found for {name}."

        summary = f"Research for {name}:\n\nTop Links:\n"
        for r in results:
            summary += f"- {r.title}: {r.url}\n"

        first_url = results[0].url
        try:
            # Fake User-Agent to look like a real browser (prevents blocking)
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

# --- PDF TOOL ---
def create_pdf(filename: str, title: str, content: str) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    # Fix encoding issues by replacing unsupported characters
    content = content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, content)
    
    if not filename.endswith(".pdf"):
        filename += ".pdf"
    
    # Save to /tmp/ if on cloud, or local folder
    # On Render, we should save to current directory or /tmp
    pdf.output(filename)
    return os.path.abspath(filename)

# --- EMAIL TOOL (SSL FIX) ---
def send_email_with_attachment(to_email: str, subject: str, body: str, attachment_path: str = None) -> bool:
    # SECURITY: Read from Environment Variables
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Error: Email credentials not set in Environment Variables.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(attachment_path)}")
            msg.attach(part)

        # *** THE FIX: Use SMTP_SSL and Port 465 ***
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False