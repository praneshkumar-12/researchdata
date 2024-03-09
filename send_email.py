import smtplib
from email.message import EmailMessage
import os


def send_email(subject, content):
    user = "clinic.management.system.service@gmail.com"
    key = "rrsfsilblgzbiaep"

    msg = EmailMessage()

    msg["Subject"] = subject

    msg["From"] = user

    msg["To"] = os.environ.get("ADMIN_EMAIL")

    msg.set_content(content)

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(user, key)
    server.send_message(msg)
    server.quit()