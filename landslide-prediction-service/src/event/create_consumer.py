from src.core.db_redis_manager.redis_query_handler import *
import redis.asyncio as redis
from fastapi import FastAPI

async def create_consumer(app:FastAPI):
    async def create_query(redis_client:redis.Redis):
        service_name = app.state.config.service_name
        try:
            await redis_client.xgroup_create(name="realtime_parameters",
                                             groupname=f"{service_name}.predictor",
                                             id="$",
                                                mkstream=True)
        except redis.ResponseError as err:
            if "BUSYGROUP" not in str(err):
                raise err

        try:
            await redis_client.xgroup_create(name="realtime_parameters",
                                                groupname=f"{service_name}.updater",
                                                id="$",
                                                mkstream=True)
        except redis.ResponseError as err:
            if "BUSYGROUP" not in str(err):
                raise err

        try:
            await redis_client.xgroup_create(name="h3_predictions",
                                                groupname=f"{service_name}.updater",
                                                id="$",
                                                mkstream=True)
        except redis.ResponseError as err:
            if "BUSYGROUP" not in str(err):
                raise err

    await query_redis(create_query, app)

