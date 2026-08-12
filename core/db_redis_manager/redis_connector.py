import redis.asyncio as redis
from fastapi import FastAPI
from src.core.config import Config
from src.core.exceptions.server_init_exceptions.redisexception import RedisConnectionException
import asyncio
'''
This module handles connection and disconnection with redis, timeouts etc.
'''
async def connectRedis(app: FastAPI):
    config:Config = app.state.config
    delay = config.retry_delay_init
    if not hasattr(config,"redis_url") or not config.redis_url:
        return
    redis_client=None
    for attempt  in range(1,config.max_retry+1):
        try:
            redis_client = redis.from_url(url=config.redis_url,
                                          encoding= "utf-8",
                                          decode_responses =True,
                                          socket_timeout=config.timeout,
                                        socket_connect_timeout=config.timeout,
                                        retry_on_timeout=True,
                                        socket_keepalive=True
                                        )
            #ping connection
            if await redis_client.ping():
                app.state.redis_client = redis_client

            return
            

        except (redis.RedisError,OSError,asyncio.TimeoutError) as err:
            if redis_client:
                await redis_client.close()
            if(attempt == config.max_retry): 
                raise RedisConnectionException()
            await asyncio.sleep(delay)
            delay *=2;


async def disconnectRedis(app: FastAPI):
    redis_client  = getattr(app.state,"redis_client",None)
    if redis_client:
        await redis_client.close()