from fastapi import FastAPI
from src.core.db_redis_manager.db_query_handler import *
from src.core.db_redis_manager.redis_query_handler import *
import asyncpg
import redis.asyncio as redis

BATCH_SIZE=10000

async def load_db_to_cache(app:FastAPI):
    async def get_from_db(conn: asyncpg.Connection):
        total_cells = await conn.fetchval("SELECT COUNT(*) FROM prediction_parameters;")
        cursor = await conn.cursor("SELECT * FROM prediction_parameters;") 
        total_fetched = 0
        while total_fetched<total_cells:
            rows = await cursor.fetch(BATCH_SIZE)
            if not rows:
                break

            async def sync_to_redis(redis_client:redis.Redis):
                pipe = redis_client.pipeline()
                for row in rows:
                    row = dict(row)
                    h3_id = row.pop("h3_index")
                    pipe.hset(f"prediction_parameters:{h3_id}", mapping = row)

                await pipe.execute()

            await query_redis(sync_to_redis,app)
            total_fetched+=len(rows)

        async def set_count(redis_client):  await redis_client.set("prediction_parameters:h3_count",total_cells)
        await query_redis(set_count,app)

    await query_db(get_from_db,app)
        


                



