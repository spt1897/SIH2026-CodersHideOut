import asyncio
from src.service.debris_propagator import propagate_debris
import redis.asyncio as redis
import json
from src.core.db_redis_manager.redis_query_handler import *
async def process(msg,service_name,app):
    msg_ids=[]
    source_cells = []
    detected_times = []
    for stream , entries in msg:
        for msg_id,data in entries:
            msg_ids.append(msg_id)
            source_cells.append(data["h3_index"])
            detected_times.append(data["time"])

    affected_cells = []
    tasks = []
    for source_cell,detection_time in zip(source_cells,detected_times):
        tasks.append(propagate_debris(source_cell,detection_time,app))

    every_affected_cells = await asyncio.gather(*tasks)

    async def send_debris_prop_result(redis_client:redis.Redis):
        pipe =redis_client.pipeline()
        for source_cell,affected_cells in zip(source_cells,every_affected_cells):
                pipe.xadd("debris_propagation_result",{
                    "source": source_cell,
                    "affected_cells" : json.dumps(affected_cells)
                })
        await pipe.execute()

    async def ack(redis_client:redis.Redis):
        await redis_client.xack("confirmed_landslide_cells",service_name,*msg_ids)

    await query_redis(send_debris_prop_result,app)
    await query_redis(ack,app)
    

    