import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_brevo_email(subject, html_content, recipient_email, recipient_name=""):
    """
    Send email using Brevo API with requests library (no brevo-python required!)
    """
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        
        # Prepare email payload
        payload = {
            "sender": {
                "email": settings.BREVO_SENDER_EMAIL,
                "name": settings.BREVO_SENDER_NAME
            },
            "to": [{
                "email": recipient_email,
                "name": recipient_name or recipient_email
            }],
            "subject": subject,
            "htmlContent": html_content
        }
        
        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json"
        }
        
        # Send email via API
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            logger.info(f"✅ Email sent successfully to {recipient_email}")
            print(f"[forgot_password] ✅ Email sent successfully to {recipient_email}")
            return True
        else:
            logger.error(f"❌ Brevo API error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            print(f"[forgot_password] ❌ API error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Request timed out")
        print("[forgot_password] ❌ Request timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        print(f"[forgot_password] ❌ Unexpected error: {e}")
        return False
