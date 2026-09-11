import py_eureka_client.eureka_client as eureka_client
import asyncio
from src.core.config import Config
from src.core.server_manager.get_server_ip import get_server_ip
from src.core.exceptions.server_init_exceptions.eurekaexception import EurekaConnectionException
from fastapi import FastAPI
import asyncio
from src.core.server_manager.server_monitor_router import heartbeat_sender
'''
This module registers the service to Eureka Service discovery server on startup
and deregisters it on shutdown as well as sends periodic heartbeats
'''

async def register_service(app:FastAPI):
    config: Config = app.state.config
    delay = config.retry_delay_init
    if not hasattr(config,"eureka_server_url") or not config.eureka_server_url:
        return
    for attempt in range(1,config.max_retry+1):
        try:
            await eureka_client.init_async(
                eureka_server=config.eureka_server_url,
                app_name=config.service_name,
                instance_host=get_server_ip(),
                instance_port=config.instance_port,
                status_page_url=f"http://{get_server_ip()}:{config.instance_port}/server/health",
                health_check_url=f"http://{get_server_ip()}:{config.instance_port}/server/health",
                metadata={
                    "active_requests" : "0",
                    "Database" : "None",
                    "Cache" : "None"
                }
            )
            
            app.state.heartbeat_sender = asyncio.create_task(heartbeat_sender(app=app,heartbeat_interval=30))
            
            return
            

        except Exception:
            if(attempt==config.max_retry):
                raise EurekaConnectionException()

            await asyncio.sleep(delay)
            delay *=2


async def deregister_service(app:FastAPI):
    config: Config = app.state.config
    delay = config.retry_delay_init
    if not hasattr(config,"eureka_server_url") or not config.eureka_server_url:
        return
    for attempt in range(1,config.max_retry+1):
        try:
            app.state.heartbeat_sender.cancel()
            try:
                await app.state.heartbeat_sender
            except asyncio.CancelledError:
                pass

            await eureka_client.stop_async()
            
            return
            

        except Exception:
            await asyncio.sleep(delay)
            delay *=2

