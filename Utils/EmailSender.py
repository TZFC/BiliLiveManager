import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from json import load

import aiosmtplib

path = os.getcwd()


async def send_mail_async(sender: str, to: list[str], subject: str, text: str, mime_text=None, image=None,
                          text_type='plain'):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(to)
    msg.attach(MIMEText(text, text_type, 'utf-8'))
    if image:
        msg.attach(MIMEText(f"<html><body><h1>{mime_text}</h1><img src='{image}'></body></html>", "html", "utf-8"))
    host = "smtp.gmail.com"
    port = 587
    smtp = aiosmtplib.SMTP(hostname=host, port=port, use_tls=False)
    await smtp.connect()
    with open(os.path.join(path, "Configs/masterConfig.json")) as mysqlFile:
        login_info = load(mysqlFile)
    await smtp.login(login_info["username"], login_info["password"])
    await smtp.send_message(msg)
    await smtp.quit()
