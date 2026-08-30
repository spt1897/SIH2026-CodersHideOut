from fastapi import FastAPI
from src.core.db_redis_manager.db_query_handler import *
from src.core.db_redis_manager.redis_query_handler import *
import asyncpg
import redis.asyncio as redis
import uuid
from src.models.h3_prediction import H3_Prediction
from src.models.realtime_parameters import RealtimeParameters

#syncs landslide probabilities to DB
async def sync_db_with_predictions(app:FastAPI):
    service_name =app.state.config.service_name
    consumer_name  = f"LPS.updater.{str(uuid.uuid4())}"
    async def read_msg(redis_client:redis.Redis):
        return await redis.xreadgroup(
            groupname=f"{service_name}.updater",
            consumername=consumer_name,
            streams={
                "h3_predictions": ">"
            },
            count=10000,
            block=5000,
        )

    async def sync_to_db(conn:asyncpg.Connection):
        query = """UPDATE prediction_parameters
            SET landslide_probability = $2 , dynamic_parameter_updated= NOW()
            WHERE h3_index=$1;"""

        await conn.executemany(query,batch)

    async def acknowledge(redis_client:redis.Redis):
        await redis_client.xack("h3_predictions", 
                          f"{service_name}.updater",
                          *msg_ids)
                

    while True:
        msg  = await query_redis(read_msg,app)

        if msg:
            batch = []
            msg_ids=[]
            for stream, entries in msg:
                for msg_id , data in entries:
                    data = H3_Prediction.model_validate(data)
                    values =tuple(data.model_dump().values())
                    batch.append(values)
                    msg_ids.append(msg_id)

            await query_db(sync_to_db,app)
            await query_redis(acknowledge,app)


#syncs realtime parameters to DB
async def sync_db_with_realtime_data(app):
    service_name =app.state.config.service_name
    consumer_name  = f"LPS.updater.{str(uuid.uuid4())}"
    async def read_msg(redis_client:redis.Redis):
            return await redis.xreadgroup(
                groupname=f"{service_name}.updater",
                consumername=consumer_name,
                streams={
                    "realtime_parameters": ">"
                },
                count=10000,
                block=5000,
            )


    async def acknowledge(redis_client:redis.Redis):
        await redis_client.xack("realtime_parameters", 
                          f"{service_name}.updater",
                          *msg_ids)

    async def sync_to_db(conn:asyncpg.Connection):
        query = """UPDATE prediction_parameters SET
                    rainfall_1h_mm =$2,
                    rainfall_3h_mm  =$3,
                    rainfall_24h_mm =$4,
                    rainfall_3d_mm =$5,
                    rainfall_7d_mm =$6,
                    soil_moisture =$7,
                    earthquake_count_7d =$8,
                    earthquake_count_30d  =$9,
                    max_earthquake_magnitude =$10,
                    distance_to_recent_earthquake_m =$11,
                    dynamic_parameter_updated = NOW()
                    WHERE h3_index = $1;"""

        await conn.executemany(query,batch)

    while True:
        msg  = await query_redis(read_msg,app)
        
        if msg:
            batch = []
            msg_ids=[]
            for stream, entries in msg:
                for msg_id , data in entries:
                    data = RealtimeParameters.model_validate(data)
                    values =tuple(data.model_dump().values())
                    batch.append(values)
                    msg_ids.append(msg_id)

            await query_db(sync_to_db,app)
            await query_redis(acknowledge,app)
            


