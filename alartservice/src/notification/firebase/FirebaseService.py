import os
import logging
import asyncio
import firebase_admin
from firebase_admin import credentials, messaging

class FirebaseService:
    _initialized = False

    @classmethod
    def initialize(cls):
        if not cls._initialized:
            try:
                cred_path = os.getenv("FIREBASE_CREDENTIALS", "resources/secret.json")
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                cls._initialized = True
                logging.info("Firebase Admin SDK initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize Firebase: {e}")

    @staticmethod
    async def push_alert(cell_id: str, score: float, msg: str = "Evacuation warning: Critical landslide threat detected."):
        if not FirebaseService._initialized:
            FirebaseService.initialize()

        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title='LANDSLIDE WARNING',
                    body=msg,
                ),
                data={
                    'cell_id': cell_id,
                    'priority_score': str(score),
                    'alert_level': 'CRITICAL'
                },
                topic=f"cell_{cell_id}" 
            )
            

            response = await asyncio.to_thread(messaging.send, message)
            logging.info(f"FCM Push successful for {cell_id}. Message ID: {response}")
            
        except Exception as e:
            logging.error(f"FCM Push failed for {cell_id}: {e}")