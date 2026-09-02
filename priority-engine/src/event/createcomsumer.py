import redis.asyncio as redis
from src.core.db_redis_manager.redis_query_handler import *

async def create_consumer(app):
    service_name = app.state.config.service_name
    async def create(redis_client:redis.Redis):
        redis_client.xgroup_create("predicted_landslide_cells",f"{service_name}",id="$",mkstream=True)
        redis_client.xgroup_create("confirmed_landslide_cells",f"{service_name}",id="$",mkstream=True)
        redis_client.xgroup_create("projected_landslide_cells",f"{service_name}",id="$",mkstream=True)

    query_redis(create,app)
    