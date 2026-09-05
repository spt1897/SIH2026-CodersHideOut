import py_eureka_client.eureka_client as eureka_client
from fastapi import FastAPI
import asyncio
import aiohttp
'''
Method for micro services to communicate among themselves,
by getting the required internal/private services IP and port from the 
Eureka server registry
'''
async def get_server_by_service(app:FastAPI,service_name:str):
    config = app.state.config
    delay =config.retry_delay_init
    for attempt in range(1,config.max_retry +1):
        try:
            servers = eureka_client.get_client().applications.get_application(service_name)

            up_servers = servers.up_instances
            if not servers or not up_servers:
                return None

            #load balance
            up_servers_by_active_clients = sorted(up_servers, key= lambda x: int(x.metadata.get("active_requests")))

            up_server_with_min_clients = up_servers_by_active_clients[0]

            return f"{up_server_with_min_clients.ipAddr}:{up_server_with_min_clients.port.port}"

        except Exception as err:
            if attempt==config.max_retry:
                raise err
            
            await asyncio.sleep(delay)
            delay *=2




async def get_http_service(app:FastAPI,service_name:str,method:str, route:str, body :dict, headers:dict):

    config = app.state.config
    delay =config.retry_delay_init
    
    url = await get_server_by_service(app,service_name=service_name)
    url = f"http://{url}{route if route.startswith("/") else f"/{route}"}"

    for attempt in range(1,config.max_retry +1):
            try:
                timeout = aiohttp.ClientTimeout(total=timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.request(
                        method=method.upper(),
                        url=url,
                        json=body if body else None,
                        headers=headers
                    ) as response:

                        return await response.json()
                
            except Exception as err:
                if attempt==config.max_retry:
                    raise err
                
                await asyncio.sleep(delay)
                delay *=2




