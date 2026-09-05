import os
from fastapi import FastAPI
import uvicorn
import asyncio
import logging
import redis.asyncio as redis
from contextlib import asynccontextmanager
from src.event.consumer import alert_consumer_loop
import py_eureka_client.eureka_client as eureka_client
from src.core.config import Config

redis_client: redis.Redis | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    logging.info("Initializing Alert Service...")

    app.state.config = Config()
    
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_client = redis.Redis(host=redis_host, port=6379, db=0)

    eureka_url = os.getenv("EUREKA_SERVER", "http://localhost:8761/eureka")
    service_port = int(os.getenv("PORT", 8001))
    
    consumer_task = asyncio.create_task(alert_consumer_loop(redis_client, app)) # type: ignore
    
    yield 

    logging.info("Executing shutdown...")
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    
    logging.info("De-coupling from Eureka")
    await eureka_client.stop_async()
    logging.info("Shutting down Redis")
    await redis_client.aclose()
    logging.info("Alert Service offline.")

app = FastAPI(title="alert-service", lifespan=lifespan)

@app.get("/health")
async def monitor_health():
    return {"status": "operational", "redis": redis_client is not None}

from fastapi import Request, Response

# @app.post("/api/v1/twilio/voice-webhook")
# async def twilio_voice_webhook(request: Request):
#     query_params = request.query_params
#     msg = query_params.get("msg", "Critical landslide threat detected. Evacuate immediately.")
#     lang_code = query_params.get("lang_code", "en-IN")

#     # Inject the dynamic message into the XML
#     twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
#     <Response>
#         <Say voice="alice" language="{lang_code}">
#             Attention. This is an alert from the Durgapur Landslide Prediction System. 
#             {msg}
#         </Say>
#         <Pause length="1"/>
#         <Say voice="alice" language="{lang_code}">Repeating. {msg}</Say>
#     </Response>
#     """
    
#     return Response(content=twiml_response, media_type="application/xml")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    uvicorn.run("src.main:app", host="0.0.0.0", port=8001, reload=False)