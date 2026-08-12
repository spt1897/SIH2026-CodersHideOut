import asyncpg
from fastapi import FastAPI
from src.core.config import Config
from src.core.exceptions.server_init_exceptions.dbexception import DBConnectionException
import asyncio
'''
This module handles connecting and disconnecting to Database
Makes sure healthy connection is established,handles timeout, retries connection
Disconnects safely at server shutdown
'''
async def connectDB(app:FastAPI):
    config: Config = app.state.config
    delay = config.retry_delay_init
    if not hasattr(config,"db_url") or not config.db_url:
        return
    db_pool =None
    for attempt in range(1,config.max_retry+1):
        try:
            #create connection pool
            db_pool =  await asyncpg.create_pool(dsn=config.db_url,
                                          min_size=config.min_db_conn,
                                          max_size=config.max_db_conn,
                                          timeout = config.timeout,
                                          command_timeout = config.timeout
                                          )

            #test connection pool
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1;")

            #put healthy connection to app.state
            app.state.db_pool = db_pool
            return
            

        except (asyncpg.PostgresError, OSError, asyncio.TimeoutError) as err:
            if db_pool:
                await db_pool.close()

            if(attempt == config.max_retry): 
                raise DBConnectionException()
            await asyncio.sleep(delay)
            delay *=2

    
    


async def disconnectDB(app:FastAPI):
    db_pool = getattr(app.state,"db_pool",None)
    if db_pool:
        await db_pool.close()