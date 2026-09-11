import aiohttp
from fastapi import FastAPI
from src.core.config import Config
from src.core.exceptions.mid_service_exceptions.sms_send_exception import SmsSendException
import asyncio
'''
Sends SMS to a phone no. , can be used for notifications.
'''


async def send_sms(phoneno_to:str,msg:str,app: FastAPI):
    
    config :Config= app.state.config
    delay  = config.retry_delay_init

    if not phoneno_to:
         raise SmsSendException("No phone no.")
    if not msg:
         raise SmsSendException("No message")

    if not phoneno_to.startswith("+91"):
         phoneno_to = ("+91"+phoneno_to).strip()

    headers={
        "authorization": "XbByVeaqcCl2mDrvgH5ThS138FLQ0xwRK67fUzWnItJPMZpA4uU1u9gLleZdkiFQ4RbaYA5DSoqtypCH",
        "accept": "application/json",
        "content-type": "application/json"
    }

    sms={
        "route": "q",
        "message": msg,
        "flash" :"0",
        "numbers": phoneno_to
    }
    http_timeout = aiohttp.ClientTimeout(total=config.timeout)
    
    async with aiohttp.ClientSession() as session:
        for attempt in range (1,config.max_retry+1):
            try:
                
                    async with session.post("https://www.fast2sms.com/dev/bulkV2", json=sms,headers=headers, timeout=http_timeout) as res:
                        if res.status not in (200,201):
                            res_json = await res.json()
                            raise SmsSendException(res_json)

                        return

            except Exception as err:
                if attempt ==config.max_retry:
                    raise SmsSendException(err)

                await asyncio.sleep(delay)
                delay *=2