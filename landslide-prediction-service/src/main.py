from fastapi import FastAPI
import uvicorn
from src.core.server_manager.server_lifespan import lifespan
from src.core.server_manager.server_monitor_router import monitor
from src.core.server_manager.server_monitor_router import conns_tracker
from src.core.server_manager.get_server_ip import get_server_ip
import asyncio
from landslide_predictor.init_model import init_model
from src.service.service import landslide_prediction_service

'''This server is not exposed publicly by any endpoint (except for monitoring),
it reads from an event bus , predicts , 
updates data and pushes to another event bus.'''

app = FastAPI(title="translation-service",lifespan=lifespan(init_model))


#Routers:
app.include_router(monitor) #monitoring route


async def main():
    async with app.router.lifespan_context(app):
        print(f"Service: '{app.state.config.service_name}' started at {get_server_ip}:{app.state.config.instance_port}")
        await landslide_prediction_service(app)
    

if __name__ == '__main__':
    asyncio.run(main())