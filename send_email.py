import smtplib
from email.message import EmailMessage
import os


def send_email(subject, content, to=None):
    user = os.environ.get("RESEARCH_MAIL_USER")
    key = os.environ.get("RESEARCH_MAIL_PASSWORD")

    msg = EmailMessage()

    msg["Subject"] = subject

    msg["From"] = user

    if to:

        msg["To"] = to
    
    else:
        msg["To"] = os.environ.get("ADMIN_EMAIL")

    msg.set_content(content)

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

    server.login(user, key)
    server.send_message(msg)
    server.quit()
