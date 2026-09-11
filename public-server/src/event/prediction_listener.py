from src.core.ws_manager.ws_conn_manager import broadcast
from src.core.db_redis_manager.redis_query_handler import *
import redis.asyncio as redis
import uuid
import asyncio
import json
import time

async def send_prediction_to_dashboard(data,app):
    msg_ids=[]
    combined_msgs = []
    json_data = {}
    json_data["metadata"] = {"type" : "broadcast", "category": "predictions"}
    for stream, entries in data:
        for msg_id,msg in entries:
            msg_ids.append(msg_id)
            msg["landslide_probability"] = float(msg["landslide_probability"])*100
            combined_msgs.append(msg)

    json_data["data"] = combined_msgs
    json_data["metadata"]["data_items"] = len(combined_msgs)
    json_data["metadata"]["timestamp"] = time.time()
    await broadcast("gis_dashboard",json_data,app)

    async def ack(redis_client:redis.Redis):
        await redis_client.xack("h3_predictions",app.state.config.service_name,*msg_ids)

    await query_redis(ack,app)


async def prediciton_listener(app):
    service_name =  app.state.config.service_name
    consumer_name  = f"PS.{uuid.uuid4()}"
    async def listen_alerts(redis_client:redis.Redis):
        return await redis_client.xreadgroup( service_name,
                                             consumername=consumer_name,
                                             streams={"h3_predictions":">"},
                                             count = 1000,
                                             block =5000)

    while True:
        data = await query_redis(listen_alerts,app)
        if not data:
            continue
        asyncio.create_task(send_prediction_to_dashboard(data,app))


