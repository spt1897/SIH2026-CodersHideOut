import redis.asyncio as redis
from src.core.db_redis_manager.redis_query_handler import query_redis
from src.service.process import process
import uuid
import asyncio

async def priority_engine(app):
    service_name = app.state.config.service_name
    consumer_name = f"PE.{uuid.uuid4()}"
    #event driven
    async def get_landslide_cells(redis_client:redis.Redis):
        return await redis_client.xreadgroup(groupname=f"{service_name}",
                                             consumername=consumer_name,
                                             streams={
                                                 "predicted_landslide_cells" : ">",
                                                 "confirmed_landslide_cells" : ">"
                                             },
                                             count = 1000,
                                             block=5000
                                             )


    while True:
        msg = await query_redis(get_landslide_cells,app)

        if not msg:
            continue

        await asyncio.create_task(process(msg,app,service_name))
        

        