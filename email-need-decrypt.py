#!/usr/bin/python3

import smtplib
from email.message import EmailMessage

# Your credentials
sender_email = ""
app_password = ""  # Gmail App Password you generated without spaces

# Email content
recipient_email = ""

subject = "please decrypt icloudpd credentials"
body = "Please run your-decrypt-command.sh on host [host].  Passphrase is [hint]."

# Create EmailMessage object
msg = EmailMessage()
msg.set_content(body)
msg["Subject"] = subject
msg["From"] = sender_email
msg["To"] = recipient_email

# Send the email via Gmail's SMTP server
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(sender_email, app_password)
    smtp.send_message(msg)

# print("Email sent successfully!")
