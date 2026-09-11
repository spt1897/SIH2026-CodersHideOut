from src.event.alert_listener import *
from src.event.debris_listener import *
from src.event.prediction_listener import *
import asyncio

async def start_event_listeners(app):
    app.state.alert_listener = asyncio.create_task(alert_listener(app))
    app.state.debris_listener = asyncio.create_task(debris_listener(app))
    app.state.prediction_listener = asyncio.create_task(prediciton_listener(app))
    print("Started event listeners.")
    

async def stop_event_listeners(app):
    app.state.alert_listener.cancel()
    app.state.debris_listener.cancel()
    app.state.prediction_listener.cancel()