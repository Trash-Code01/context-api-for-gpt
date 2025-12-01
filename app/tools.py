import base64

# ... keep imports at the top ...

# --- NEW API EMAIL TOOL (BREVO) ---
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