import os
import smtplib
from email.message import EmailMessage
from utils import get_xlsx_filepath
from datetime import datetime

def get_current_quarter(date_obj) -> str:
    return f"Q{(date_obj.month - 1) // 3 + 1}"


def email_title(title: str) -> str:
    now = datetime.now()
    return f"[Automation Summary] {title} {get_current_quarter(now)} Report"

# Get the secret from environment variables
EMAIL_FROM = os.environ.get('EMAIL_USERNAME')
EMAIL_TO = os.environ.get('EMAIL_DEV')
PASSWORD = os.environ.get('EMAIL_PASSWORD')
filename = "hl.xlsx"
FILE = get_xlsx_filepath(filename)
# Create Message
msg = EmailMessage()
msg['Subject'] = email_title("Hargreaves Lansdown")
msg['From'] = f"Amine Upwork <{EMAIL_FROM}>"
msg['To'] = EMAIL_TO
msg.set_content("Please see attached spreadsheet.")

# Attach File (Example: PDF)
with open(FILE, 'rb') as f:
    print(FILE)
    file_data = f.read()
    msg.add_attachment(file_data, maintype='application',
                       subtype='xlsx', filename=filename)

# Send via SMTP_SSL
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    if EMAIL_FROM and PASSWORD:
        smtp.login(EMAIL_FROM, PASSWORD)
        smtp.send_message(msg)
