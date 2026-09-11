from src.core.ws_manager.ws_conn_manager import broadcast
from src.core.db_redis_manager.redis_query_handler import *
import redis.asyncio as redis
import uuid
import asyncio
import json
import time
from src.event.road_datas import *

async def send_alert_to_dashboard(data,app):
    msg_ids=[]
    combined_msgs = []
    json_data = {}
    cells=[]
    types=[]
    json_data["metadata"] = {"type" : "broadcast", "category": "alerts"}
    for stream, entries in data:
        for msg_id,msg in entries:
            msg_ids.append(msg_id)
            msg["priority_score"] = float(msg["priority_score"])
            cells.append(msg["cell_id"])
            types.append(msg["type"])
            combined_msgs.append(msg)

    json_data["data"] = combined_msgs
    json_data["metadata"]["data_items"] = len(combined_msgs)
    json_data["metadata"]["timestamp"] = time.time()

    road_datas = get_affected_roads(cells,types,app)

    await broadcast("gis_dashboard",json_data,app)
    await broadcast("gis_dashboard",road_datas,app)

    async def ack(redis_client:redis.Redis):
        await redis_client.xack("dashboard_alert_stream",app.state.config.service_name,*msg_ids)

    await query_redis(ack,app)


async def alert_listener(app):
    service_name =  app.state.config.service_name
    consumer_name  = f"PS.{uuid.uuid4()}"
    async def listen_alerts(redis_client:redis.Redis):
        return await redis_client.xreadgroup(service_name,
                                             consumername=consumer_name,
                                             streams={"dashboard_alert_stream":">"},
                                             count = 1000,
                                             block =5000)

    while True:
        data = await query_redis(listen_alerts,app)
        if not data:
            continue
        asyncio.create_task(send_alert_to_dashboard(data,app))
