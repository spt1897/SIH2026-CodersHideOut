from fastapi import FastAPI,WebSocket,APIRouter,WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from src.core.ws_manager.ws_conn_manager import *
from src.service.gis_service.service import gis_service

dashboard = APIRouter(prefix="/dashboard")

@dashboard.websocket("/gis")
async def gis_dashboard(ws: WebSocket):
    app = ws.app
    room = "gis_dashboard"
    await ws_connect(ws,room,app)

    try:
        while True:
            req = await ws.receive_json()

            res  = await gis_service(req,app)
            
            if res:
                await ws.send_json(jsonable_encoder(res))

    except WebSocketDisconnect:
        await ws_disconnect(ws,room,app)
