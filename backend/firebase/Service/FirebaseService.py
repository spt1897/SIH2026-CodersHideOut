import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import firebase_admin
from firebase_admin import credentials, messaging
import py_eureka_client.eureka_client as eureka_client
from fastapi import FastAPI, BackgroundTasks, Request, HTTPException
from contextlib import asynccontextmanager
from Model.DataModels import TokenAlert
from Model.DataModels import TopicAlert
from Model.DataModels import LandslideAlert
from Model.DataModels import SubscriptionRequest
import uvicorn
import h3

REST_PORT = 8000
EUREKA_SERVER = "http://localhost:8761/eureka"
APP_NAME = "NOTIFICATION-SERVICE"

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if not os.path.exists("backend\\firebase\\resources\\secret.json"):
            print("ERROR: secret.json not found! Firebase will not work.")
        else:
            cred = credentials.Certificate("backend\\firebase\\resources\\secret.json")
            firebase_admin.initialize_app(cred)
            print("Firebase initialized successfully.")
    except Exception as e:
        print(f"Warning: Firebase initialization failed. Error: {e}")

    try:
        await eureka_client.init_async(
            eureka_server=EUREKA_SERVER,
            app_name=APP_NAME,
            instance_port=REST_PORT,
        )
        print(f"Successfully registered {APP_NAME} with Eureka.")
    except Exception as e:
        print(f"Warning: Eureka registration failed. Error: {e}")
    
    yield 

    try:
        await eureka_client.stop_async()
        print("Unregistered from Eureka.")
    except Exception as e:
        print(f"Error during Eureka shutdown: {e}")

app = FastAPI(lifespan=lifespan)

def push_to_firebase_topic(alert: TopicAlert):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=alert.title,
                body=alert.body,
            ),
            data={"severity": alert.severity, "type": "topic_alert"},
            topic=alert.topic,
        )
        response = messaging.send(message)
        print(f"FCM Topic Send Success: {response}")
    except Exception as e:
        print(f"FCM Topic Send Failed: {e}")

def push_to_firebase_token(alert: TokenAlert):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=alert.title,
                body=alert.body,
            ),
            data={"severity": alert.severity, "type": "direct_alert"},
            token=alert.token,
        )
        response = messaging.send(message)
        print(f"FCM Direct Send Success: {response}")
    except Exception as e:
        print(f"FCM Direct Send Failed: {e}")

def push_to_firebase_In_hex_area(alert: LandslideAlert):
    try:
        center_hex = h3.latlng_to_cell(alert.latitude, alert.longitude, 8)

        affected_hexagons = h3.grid_disk(center_hex, alert.danger_radius_in_hexagons)
        
        for hex_id in affected_hexagons:
            topic_name = f"alert_hex_{hex_id}"
            message = messaging.Message(
                notification=messaging.Notification(
                    title=alert.title,
                    body=alert.body,
                ),
                data={"severity": alert.severity, "type": "hex_alert"},
                topic=topic_name,
            )
            response = messaging.send(message)
            print(f"FCM Hex Topic Send Success for {topic_name}: {response}")
            print(f"FCM Hex Topic Send Success: {topic_name}")
            
    except Exception as e:
        print(f"FCM Hex Send Failed: {e}")

@app.post("/internal/alerts/area", status_code=202)
async def dispatch_hex_alert(alert: LandslideAlert, background_tasks: BackgroundTasks, request: Request):
    background_tasks.add_task(push_to_firebase_In_hex_area, alert)
    return {"status": "queued", "type": "hex_grid", "center": f"{alert.latitude},{alert.longitude}"}

@app.post("/internal/alerts/topic", status_code=202)
async def dispatch_topic_alert(alert: TopicAlert, background_tasks: BackgroundTasks, request: Request):
    background_tasks.add_task(push_to_firebase_topic, alert)
    return {"status": "queued", "type": "topic", "target": alert.topic}

@app.post("/internal/alerts/direct", status_code=202)
async def dispatch_direct_alert(alert: TokenAlert, background_tasks: BackgroundTasks, request: Request):
    background_tasks.add_task(push_to_firebase_token, alert)
    return {"status": "queued", "type": "direct"}

@app.post("/internal/alerts/subscribe", status_code=200)
async def subscribe_user_to_topic(req: SubscriptionRequest):
    try:
        response = messaging.subscribe_to_topic([req.token], req.topic)
        print(f"Subscribed token to {req.topic}: {response.success_count} success")
        return {"status": "success", "topic": req.topic}
    except Exception as e:
        print(f"Subscription Failed: {e}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=REST_PORT)