from typing import Callable,TypeVar,Any
from fastapi import FastAPI
from src.core.config import Config
import asyncpg
import asyncio
from src.core.exceptions.mid_service_exceptions.failed_db_operation_exception import FailedDBOperationException

async def query_db(query_func: Callable[[asyncpg.Connection],Any],app: FastAPI):
    config:Config = app.state.config
    db_pool = getattr(app.state,"db_pool",None)
    if not db_pool:
        return

    delay = config.retry_delay_init

    for attempt in range(1,config.max_retry+1):
        try:
            async with db_pool.acquire() as conn:
                async with conn.transaction():
                    return await query_func(conn)
        except (asyncpg.PostgresSyntaxError,asyncpg.NotNullViolationError,asyncpg.UniqueViolationError, asyncpg.ForeignKeyViolationError) as err:
            raise err

        except Exception as err:
            if attempt == config.max_retry:
                raise FailedDBOperationException(err)
            await asyncio.sleep(delay)
            delay *= 2
