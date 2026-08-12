import aiosmtplib
from email.message import EmailMessage
from fastapi import FastAPI
from src.core.config import Config
from src.core.exceptions.mid_service_exceptions.email_send_exception import EmailSendException
import asyncio

async def send_email(address_to:str,subject:str, email_body:str,app: FastAPI):
    
    config :Config= app.state.config
    delay  = config.retry_delay_init
    email =EmailMessage()
    email["From"] = config.smtp_address_from
    email["To"] =address_to
    email["Subject"] = subject
    email.set_content(email_body)

    for attempt in range (1,config.max_retry+1):
        try:
            await aiosmtplib.send(
            email,
            hostname=config.smtp_host,
            port=config.smtp_port,
            username=config.smtp_username,
            password=config.smtp_password,
            start_tls=True,
            smtputf8=True,
            timeout=config.timeout,
            )

            return

        except Exception as err:
            if attempt ==config.max_retry:
                raise EmailSendException(err)

            await asyncio.sleep(delay)
            delay *=2
        




