import aiohttp
import asyncio
import logging
from src.core.config import Config
from src.core.exceptions.mid_service_exceptions.voice_call_exception import VoiceCallException

class VoiceCallService:
    @staticmethod
    async def send_voicecall(phoneno_to: str, msg: str, lang_code: str, config: Config):
        delay = config.retry_delay_init

        print(f"DEBUG SID: {config.twilio_account_sid}")
        print(f"DEBUG TOKEN: {config.twilio_auth_token[:4]}...")

        twiml_instructions = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<Response>\n'
            f'    <Say voice="Polly.Aditi" language="{lang_code}">\n'
            f'        Attention. This is an alert from the Landslide Prediction System.\n'
            f'        {msg}\n'
            f'    </Say>\n'
            f'    <Pause length="1"/>\n'
            f'    <Say voice="Polly.Aditi" language="{lang_code}">Repeating. {msg}</Say>\n'
            f'</Response>'
        ).strip()

        call_data = {
            "To": phoneno_to,
            "From": config.twilio_phone_no,
            "Twiml": twiml_instructions, # <--- THIS BYPASSES THE WEBHOOK
        }

        http_timeout = aiohttp.ClientTimeout(total=config.timeout)
        auth = aiohttp.BasicAuth(login=config.twilio_account_sid, password=config.twilio_auth_token)
        twilio_url = f"https://api.twilio.com/2010-04-01/Accounts/{config.twilio_account_sid}/Calls.json"

        async with aiohttp.ClientSession() as session:
            for attempt in range(1, config.max_retry + 1):
                try:
                    async with session.post(twilio_url, data=call_data, auth=auth, timeout=http_timeout) as res:
                        if res.status not in (200, 201):
                            error_text = await res.text()
                            raise VoiceCallException(f"Twilio API Error: {res.status} - {error_text}")

                        logging.info(f"Voice call successfully dispatched to {phoneno_to}")
                        return

                except Exception as err:
                    logging.warning(f"Voice call attempt {attempt}/{config.max_retry} failed for {phoneno_to}: {err}")
                    
                    if attempt == config.max_retry:
                        logging.error(f"Max retries reached. Failed to send voice call to {phoneno_to}")
                        raise VoiceCallException(err)

                await asyncio.sleep(delay)
                delay *= 2