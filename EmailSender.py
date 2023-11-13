import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from json import load
async def send_mail_async(sender:str, to:list[str], subject:str, text:str, textType='plain'):
    msg = MIMEMultipart()
    msg.preamble = subject
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(to)
    msg.attach(MIMEText(text, textType, 'utf-8'))
    host = "smtp.gmail.com"
    port = 587
    smtp = aiosmtplib.SMTP(hostname=host, port=port, use_tls=False)
    await smtp.connect()
    login_info = load(open("Configs/masterConfig.json"))
    await smtp.login(login_info["username"], login_info["password"])
    await smtp.send_message(msg)
    await smtp.quit()