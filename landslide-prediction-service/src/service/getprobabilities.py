from fastapi import FastAPI
import redis.asyncio as redis
from src.core.db_redis_manager.redis_query_handler import *
from src.models.realtime_parameters import *
from src.models.features import *
from src.models.staticfeatures import *
from src.models.h3_prediction import *
import asyncio
from src.landslide_predictor.predict import *

async def getprobabilities(msg,app:FastAPI):
    async def getstaticfeatures(redis_client:redis.Redis):
        pipe = redis_client.pipeline()
        for h3_index in h3_indexes:
            pipe.hgetall(f"prediction_parameters:{h3_index}")
        return await pipe.execute()

    msg_ids = []
    realtime_param_batch= []
    for stream, entries in msg:
        for msg_id , data in entries:
            msg_ids.append(msg_id)
            data = RealtimeParameters.model_validate(data).model_dump()
            realtime_param_batch.append(data)

    h3_indexes = []
    for realtime_param in realtime_param_batch:
        h3_indexes.append(realtime_param["h3_index"])

    res = await query_redis(getstaticfeatures,app)

    static_features = []
    for r in res:
        static_features.append(StaticFeatures.model_validate(r).model_dump())

    features_batch = []
    for i in range(len(h3_indexes)):
        feature_vector = list(Features(**static_features[i],**realtime_param_batch[i]).model_dump().values())
        features_batch.append(feature_vector)

    loop = asyncio.get_running_loop()
    pool= app.state.process_pool

    return await loop.run_in_executor(pool,predict,features_batch) , h3_indexes,msg_ids

