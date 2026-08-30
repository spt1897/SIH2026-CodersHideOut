from src.service.getprobabilities import *
from src.service.pushprobabilities import *

async def process(msg,app,groupname):
    probabilities,h3_indexes,msg_ids = await getprobabilities(msg,app)
    await pushprobabilities(h3_indexes,probabilities,app)

    async def ack(redis_client:redis.Redis):
        await redis_client.xack("realtime_parameters",groupname,*msg_ids)

    await query_redis(ack,app)

