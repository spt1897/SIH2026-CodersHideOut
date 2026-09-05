import logging

import asyncio
import logging
from fastapi import FastAPI
from src.core.config import Config
from src.notification.telecom.voicecall_sender import VoiceCallService
from src.notification.firebase.FirebaseService import FirebaseService as web


async def push_twilio_sms(h3_index: str, probability: float):
    # Twilio logic remains stubbed for now
    """
    --------- NOT IN USE ----------
    """

    logging.warning(f"[SIMULATION] Twilio SMS dispatched for grid {h3_index}")

async def push_firebase_notification(h3_index: str, probability: float, msg: str):
    """
    Executes the live Firebase push notification.
    """

    await web.push_alert(cell_id=h3_index, score = probability, msg=msg)


async def push_email_alert(h3_index: str, probability: float):
    logging.warning(f"[SIMULATION] Email dispatched for grid {h3_index}")

async def push_twilio_voice(h3_index: str, probability: float, app: FastAPI):
    """
    Executes the live Twilio Voice Call notification.
    """
    config: Config = app.state.config
    mock_target_phones = ["+917001510172"]
    alert_message = (
        f"Critical Alert. Evacuation warning. "
        f"Grid {h3_index} has reached a severe landslide threat score of {probability:.2f}. "
        f"Please take immediate precautions."
    )
    
    tasks = [
        VoiceCallService.send_voicecall(
            phoneno_to=phone,
            msg=alert_message,
            lang_code="en-IN",
            config=config
        )
        for phone in mock_target_phones
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for phone, res in zip(mock_target_phones, results):
        if isinstance(res, Exception):
            logging.error(f"Voice call failed for {phone}: {res}")
        else:
            logging.info(f"Voice call confirmed dispatched to {phone}")

    logging.warning(f"[NOTIFICATION] Voice call batch dispatched for grid {h3_index} to {mock_target_phones}")