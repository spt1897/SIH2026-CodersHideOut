'''Sample main function setup for microservice'''
from fastapi import FastAPI
import uvicorn
from src.core.server_manager.server_lifespan import lifespan
from src.core.server_manager.server_monitor_router import monitor
from src.core.server_manager.server_monitor_router import conns_tracker
from src.core.server_manager.get_server_ip import get_server_ip
import asyncio
from src.service.service import *

app = FastAPI(title="translation-service",lifespan=lifespan())


#Routers:
app.include_router(monitor)
#Middlewares:
#asgi wrapper middlewares:
app.add_middleware(conns_tracker)


async def main():
    async with app.router.lifespan_context(app):
        print(f"Service: {app.state.config.service_name} started on {get_server_ip}:{app.state.config.instance_port}")
        await priority_engine()

if __name__ == '__main__':
    asyncio.run(main())