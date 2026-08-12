import aiohttp
from fastapi import FastAPI
from src.core.config import Config
from src.core.exceptions.mid_service_exceptions.sms_send_exception import SmsSendException
import asyncio

async def send_sms(phoneno_to:str,msg:str,app: FastAPI):
    
    config :Config= app.state.config
    delay  = config.retry_delay_init

    sms={
        "To": phoneno_to,
        "From": config.twilio_phone_no,
        "Body": msg
    }
    http_timeout = aiohttp.ClientTimeout(total=config.timeout)
    auth = aiohttp.BasicAuth(login=config.twilio_account_sid,password=config.twilio_auth_token)

    async with aiohttp.ClientSession() as session:
        for attempt in range (1,config.max_retry+1):
            try:
                
                    async with session.post(f"https://api.twilio.com/2010-04-01/Accounts/{config.twilio_account_sid}/Messages.json", data=sms, auth=auth, timeout=http_timeout) as res:
                        if res.status not in (200,201):
                            raise SmsSendException()

                        return

            except Exception as err:
                if attempt ==config.max_retry:
                    raise SmsSendException(err)

                await asyncio.sleep(delay)
                delay *=2