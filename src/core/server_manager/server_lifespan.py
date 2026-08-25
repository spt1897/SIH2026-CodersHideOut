from contextlib import asynccontextmanager
from src.core.server_manager.service_registry import register_service, deregister_service
from src.core.db_redis_manager.db_connector import connectDB, disconnectDB
from src.core.db_redis_manager.redis_connector import connectRedis, disconnectRedis
from src.core.server_manager.loadenv import loadenv
from src.core.config import Config
from src.core.server_manager.appstate import init_appstate
from fastapi import FastAPI
from typing import Callable
import time
'''
This file manages the lifespan(initiialization and deinitialisation) of the server.
Sets up the server by connecting to DB,cache,and registering to Eureka on startup
and deregistering, disconnecting on shutdown.
'''
async def init_server(app: FastAPI,process_pool_init:Callable=None,args:tuple[()]=None):
    #Create the config object and initialise it with .env variables
    app.state.config = Config()
    loadenv(app)
    #connect to DB and redis
    await connectDB(app)
    await connectRedis(app)
    #initialise other app state variables
    await init_appstate(app,process_pool_init,args)
    #register to eureka now
    await register_service(app)
   


async def deinit_server(app: FastAPI):
    #deregister from eureka first
    await deregister_service(app)
    #disconnect from DB and redis
    await disconnectDB(app)
    await disconnectRedis(app)


def lifespan(process_pool_init:Callable=None,args:tuple[()]=None):
    @asynccontextmanager
    async def _lifespan(app: FastAPI):
        await init_server(app,process_pool_init,args)
        try:
            yield
        finally:
            await deinit_server(app)

    return _lifespan