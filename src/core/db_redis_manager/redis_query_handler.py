from typing import Callable, TypeVar, Any
from fastapi import FastAPI
from src.core.config import Config
import redis.asyncio as redis
import asyncio
from src.core.exceptions.mid_service_exceptions.failed_cache_operation_exception import FailedCacheOperationException


async def query_redis(query_func :Callable[[redis.Redis],Any],app:FastAPI):
    config:Config = app.state.config
    delay =config.retry_delay_init

    redis_client :redis= getattr(app.state,"redis_client",None)

    if not redis_client:
        return

    for attempt in range(1,config.max_retry+1):
        try:
            return await query_func(redis_client)

        except redis.ResponseError as err:
            return err

        except Exception:
            if attempt==config.max_retry:
                raise FailedCacheOperationException()
            await asyncio.sleep(delay)
            delay*=2
