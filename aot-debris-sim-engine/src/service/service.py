import redis.asyncio as redis
from src.core.db_redis_manager.redis_query_handler import *
import uuid
import asyncio
from src.service.process import process

async def aot_debris_prop_service(app):
    config = app.state.config
    service_name = config.service_name
    consumer_name = f"DPE.{uuid.uuid4()}"
    async def get_realtime_data(redis_client:redis.Redis):
        return await redis_client.xreadgroup(groupname=f"{service_name}",
                                             consumername=consumer_name,
                                             streams={
                                                 "confirmed_landslide_cells" : ">"
                                             },
                                             count = 1000,
                                             block=5000
                                             )


    while True:
        msg = await query_redis(get_realtime_data,app)

        if not msg:
            continue

        await asyncio.create_task(process(msg,service_name,app))
        