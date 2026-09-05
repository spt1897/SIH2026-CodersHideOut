import aiosmtplib
from email.message import EmailMessage
from fastapi import FastAPI
from src.core.config import Config
from src.core.exceptions.mid_service_exceptions.email_send_exception import EmailSendException
import asyncio
import aiofiles
import os
import mimetypes

'''
Sends Email to any Email address(supported with files) via SMTP server.
'''



async def send_email(address_to:str,subject:str, email_body:str,files:list[str], app: FastAPI):
    
    config :Config= app.state.config
    delay  = config.retry_delay_init
    email =EmailMessage()
    email["From"] = config.smtp_address_from
    email["To"] =address_to
    email["Subject"] = subject
    email.set_content(email_body)

    if files:
        for file in files:
            if not os.path.exists(file):
                continue

            content_type, encoding = mimetypes.guess_type(file)
            if content_type is None or encoding is not None:
                content_type = "application/octet-stream"
            
            maintype, subtype = content_type.split("/", 1)

            async with aiofiles.open(file, "rb") as f:
                file_data = await f.read()

            filename = os.path.basename(file)

            email.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=filename
            )

    for attempt in range (1,config.max_retry+1):
        try:
            await aiosmtplib.send(
            email,
            hostname=config.smtp_host,
            port=config.smtp_port, # type: ignore
            username=config.smtp_username,
            password=config.smtp_password,
            use_tls=True,
            #smtputf8=True,
            timeout=config.timeout,
            )

            return

        except Exception as err:
            if attempt ==config.max_retry:
                raise EmailSendException(err)

            await asyncio.sleep(delay)
            delay *=2
        

