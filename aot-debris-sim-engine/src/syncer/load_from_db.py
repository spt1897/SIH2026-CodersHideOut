from src.core.db_redis_manager.redis_query_handler import *
from src.core.db_redis_manager.db_query_handler import *
import asyncpg
import redis.asyncio as redis

BATCH_SIZE =10000

async def load_from_db(app):
    async def get_from_db(conn: asyncpg.Connection):
        total_cells = await conn.fetchval("SELECT COUNT(*) FROM simulation_cell_state;")
        cursor = await conn.cursor("SELECT * FROM simulation_cell_state;") 
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
                    pipe.hset(f"cell_sim_nodes:{h3_id}", mapping = row)
