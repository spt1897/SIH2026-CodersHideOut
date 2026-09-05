import redis.asyncio as redis
from src.core.db_redis_manager.redis_query_handler import *

async def createconsumer(app):
    service_name = app.state.config.service_name
    async def create(redis_client:redis.Redis):
        await redis_client.xgroup_create("confirmed_landslide_cells",groupname=service_name,
                                         id="$", mkstream=True)

    await query_redis(create,app)
    