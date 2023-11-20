import smtplib
import ssl
import mimetypes
from email.message import EmailMessage

from . import config as cfg
from . import logger as log

async def send (to, subject, message="", attachments=[]):

    mailfrom = f"{cfg.tool_name} <{cfg.email_from}>"

    # prepare the email
    # msg = EmailMessage()
    # msg['Subject'] = subject
    # msg['From'] = mailfrom
    # msg['To'] = ", ".join(to)
    # msg.set_content(message)
    # msg.add_alternative(f"<pre>{message}</pre>")
    # for attachment in attachments:
    #     try:
    #         name = attachment['name']
    #         data = attachment['data']

    #         # find the file type
    #         ctype, encoding = mimetypes.guess_type(name)
    #         if ctype is None or encoding is not None:
    #             ctype = 'application/octet-stream'
    #         maintype, subtype = ctype.split('/', 1)
    #         msg.add_attachment(data.encode(),
    #                            maintype=maintype,
    #                            subtype=subtype,
    #                            filename=name)
    #     except Exception as e:
    #         await log.error(f"Error sending email: {e}", "config")
    #         return

    message = '\n'.join([f"From: {mailfrom}", f"Subject: {subject}", message])
    # send the email
    with smtplib.SMTP_SSL(cfg.email_host, cfg.email_port, context=ssl.create_default_context()) as server:
        server.connect(f"{cfg.email_host}:{cfg.email_port}")
        server.login(cfg.email_user, cfg.email_password)
        server.sendmail(mailfrom, to, message)
