# stock_check.py
import os
import re
import requests
import smtplib
from email.message import EmailMessage

PART_NUMBER = os.environ.get("PART_NUMBER", "")
ZIPCODE = os.environ.get("ZIPCODE", "")
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")
EMAIL_TO   = os.environ.get("EMAIL_TO", EMAIL_USER)

def check_stock(part, zipc):
    url = "https://www.apple.com/shop/fulfillment-messages"
    params = {"parts.0": part, "zip": zipc}
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    text = r.text.lower()
    # find "available" that is NOT part of "unavailable"
    return bool(re.search(r'(?<!un)available', text)), text

def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_TO
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

if __name__ == "__main__":
    if not PART_NUMBER or not ZIPCODE or not EMAIL_USER or not EMAIL_PASS:
        print("Missing required environment variables (PART_NUMBER, ZIPCODE, EMAIL_USER, EMAIL_PASS).")
        raise SystemExit(1)
    try:
        available, raw = check_stock(PART_NUMBER, ZIPCODE)
        if available:
            send_email(
                f"IN STOCK: {PART_NUMBER} near {ZIPCODE}",
                f"Good news — your part may be available!\n\nOpen the Apple product page and check availability with your ZIP.\n\nResponse snippet:\n\n{raw[:1600]}"
            )
            print("Email sent: AVAILABLE")
        else:
            print("Not available right now.")
    except Exception as e:
        print("Error:", str(e))
        raise
