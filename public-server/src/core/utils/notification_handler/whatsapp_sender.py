import aiohttp
import asyncio
from fastapi import FastAPI
from src.core.exceptions.mid_service_exceptions.whatsapp_send_exception import WhatsappSendException
from src.core.config import Config

'''
Sends whatsapp msg or files to a whatsapp no.
'''


async def send_whatsapp_msg(whatsapp_number_to:str, msg:str ,media_url:str=None, app = FastAPI()):
    
    config :Config= app.state.config
    delay  = config.retry_delay_init

    whatsapp={
         "Content-Type":"application/x-www-form-urlencoded",
        "To": f"whatsapp:{whatsapp_number_to}",
        "From": config.twilio_whatsapp_no,
        "ContentSid":"HXfe5ab5f00277942d4d4200328b4d403c",
        "Body": msg
    }

    if media_url:
         whatsapp["media"] = media_url

    http_timeout = aiohttp.ClientTimeout(total=config.timeout)
    auth = aiohttp.BasicAuth(login=config.twilio_account_sid,password=config.twilio_auth_token)

    async with aiohttp.ClientSession() as session:
        for attempt in range (1,config.max_retry+1):
            try:
                
                    async with session.post(f"https://api.twilio.com/2010-04-01/Accounts/{config.twilio_account_sid}/Messages.json", data=whatsapp, auth=auth, timeout=http_timeout) as res:
                        if res.status not in (200,201):
                            res_json = await res.json()
                            raise WhatsappSendException(res_json.get("code"))

                        return

            except Exception as err:
                if attempt ==config.max_retry:
                    raise WhatsappSendException(err)

                await asyncio.sleep(delay)
                delay *=2   