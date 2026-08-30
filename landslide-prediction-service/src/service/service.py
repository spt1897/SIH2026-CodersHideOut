from fastapi import FastAPI
import redis.asyncio as redis
import uuid
from src.core.db_redis_manager.redis_query_handler import *
import asyncio
from src.service.process import *

async def landslide_prediction_service(app:FastAPI):
    service_name = app.state.config.service_name
    consumer_name = f"LPS.predictor.{uuid.uuid4()}"
    #event driven
    async def get_realtime_data(redis_client:redis.Redis):
        return await redis_client.xreadgroup(groupname=f"{service_name}.predictor",
                                             consumername=consumer_name,
                                             streams={
                                                 "realtime_parameters" : ">"
                                             },
                                             count = 1000,
                                             block=5000
                                             )


    while True:
        msg = await query_redis(get_realtime_data,app)

        if not msg:
            continue
        asyncio.create_task(process(msg,app,f"{service_name}.predictor"))




        

        



        
        

        


        

        
