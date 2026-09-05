import uuid
import asyncio
import logging
import redis.asyncio as redis
from src.service.processor import evaluate_batch
from fastapi import FastAPI

async def alert_consumer_loop(redis_pool: redis.Redis,app: FastAPI):
    service_name = "alert_service"
    consumer_name = f"{service_name}.dispatcher.{uuid.uuid4()}"
    group_name = f"{service_name}.consumer_group"
    
    try:
        await redis_pool.xgroup_create(name="priority_cells_stream", groupname=group_name, id="0", mkstream=True)
    except redis.ResponseError as err:
        if "BUSYGROUP" not in str(err):
            raise err

    logging.info(f"Alert Consumer '{consumer_name}' entering polling loop...")

    while True:
        try:
            msg_batch = await redis_pool.xreadgroup(
                groupname=group_name,
                consumername=consumer_name,
                streams={"priority_cells_stream": ">"},
                count=10,
                block=2000
            )
            
            if not msg_batch:
                continue


            await evaluate_batch(msg_batch, redis_pool, group_name,app)
            
        except Exception as e:
            logging.error(f"Consumer loop error: {e}")
            await asyncio.sleep(1) 