import smtplib
from email.message import EmailMessage
import mimetypes

from . import config as cfg
from . import logger as log

async def send (to, subject, message="", attachments=[]):

    mailfrom = f"{cfg.tool_name} <noreply@flockpocket.com>"

    # prepare the email
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = mailfrom
    msg['To'] = ", ".join(to)
    msg.set_content(message)
    msg.add_alternative(f"<pre>{message}</pre>")
    for attachment in attachments:
        try:
            name = attachment['name']
            data = attachment['data']

            # find the file type
            ctype, encoding = mimetypes.guess_type(name)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            msg.add_attachment(data.encode(),
                               maintype=maintype,
                               subtype=subtype,
                               filename=name)
        except Exception as e:
            await log.error(f"Error sending email: {e}", "config")
            return

    # send the email
    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)

