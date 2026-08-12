import aiohttp
from fastapi import FastAPI
from src.core.config import Config
from src.core.exceptions.mid_service_exceptions.voice_call_exception import VoiceCallException
import asyncio

async def send_voicecall(phoneno_to:str,msg:str,lang_code:str,app: FastAPI):
    
    config :Config= app.state.config
    delay  = config.retry_delay_init

    data = f'<Response><Say language="{lang_code}">{msg}</Say></Response>'

    call={
            "To": phoneno_to,
            "From": config.twilio_phone_no,
            "Twiml": data
        }

    http_timeout = aiohttp.ClientTimeout(total=config.timeout)
    auth = aiohttp.BasicAuth(login=config.twilio_account_sid,password=config.twilio_auth_token)
    async with aiohttp.ClientSession() as session:
        for attempt in range (1,config.max_retry+1):
            try:
           
                async with session.post(f"https://api.twilio.com/2010-04-01/Accounts/{config.twilio_account_sid}/Calls.json", data=call, auth=auth, timeout=http_timeout) as res:
                    if res.status not in (200,201):
                        raise VoiceCallException()

                    return

            except Exception as err:
                if attempt ==config.max_retry:
                    raise VoiceCallException(err)

                await asyncio.sleep(delay)
                delay *=2