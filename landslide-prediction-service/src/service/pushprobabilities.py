import redis.asyncio as redis
from src.core.db_redis_manager.redis_query_handler import query_redis

async def pushprobabilities(h3_indexes,probabilities,app):
    landslide_cells = []
    allcells = []
    for h3_index, probability in zip(h3_indexes,probabilities):
        if probability>0.5:
            landslide_cells.append({
                "h3_index" : h3_index,
                "landslide_probability" : probability
            })

        allcells.append({
            "h3_index" : h3_index,
            "landslide_probability" : probability
        })

    async def streamtoredis(redis_client:redis.Redis):
        pipe = redis_client.pipeline()
        for landslide_cell in landslide_cells:
            pipe.xadd( "landslide_cells",landslide_cell)
        for cell in allcells:
            pipe.xadd("h3_predictions", cell)
        await pipe.execute()

    await query_redis(streamtoredis,app)


    
