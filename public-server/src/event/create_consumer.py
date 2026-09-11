import redis.asyncio as redis
from src.core.db_redis_manager.redis_query_handler import *

async def createconsumer(app):
    service_name = app.state.config.service_name
    async def create(redis_client:redis.Redis):
        try:
            await redis_client.xgroup_create("debris_propagation_result",groupname=service_name,
                                         id="$", mkstream=True)
            await redis_client.xgroup_create("h3_predictions",groupname=service_name,
                                                     id="$", mkstream=True)
            await redis_client.xgroup_create("dashboard_alert_stream",groupname=service_name,
                                                     id="$", mkstream=True)
            
            
    
        except redis.ResponseError as err:
            if "BUSYGROUP" not in str(err):
                raise err

    await query_redis(create,app)
    