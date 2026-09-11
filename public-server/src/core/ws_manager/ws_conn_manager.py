from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
async def ws_connect(ws:WebSocket,room:str,app):
    await ws.accept()
    if not hasattr(app.state.ws_connections,room):
        setattr(app.state.ws_connections,room,set())

    client_set = getattr(app.state.ws_connections,room)
    client_set.add(ws)

async def ws_disconnect(ws:WebSocket,room,app):
    if not hasattr(app.state.ws_connections,room):
        return

    client_set = getattr(app.state.ws_connections,room)
    if ws in client_set:
        client_set.discard(ws)

async def broadcast(room,msg,app):
    if not hasattr(app.state.ws_connections,room):
        return
    client_set = getattr(app.state.ws_connections,room)
    expired_clients = set()
    for ws in client_set:
        try:
            await ws.send_json(jsonable_encoder(msg))
        except WebSocketDisconnect:
            expired_clients.add(ws)
        except Exception as err:
            print(str(err))

    for ws in expired_clients:
        await ws_disconnect(ws,room,app)


