from fastapi import FastAPI,APIRouter, status, Request,Response
import asyncio
import time
import py_eureka_client.eureka_client as eureka_client
'''
This module is dedicated to health checks , heartbeats and monitoring the
microservice to ensure its proper working. It routes all server monitoring apis
'''
monitor = APIRouter(prefix="/server",tags=["Server-Monitoring"])

#asgi middle-ware to track number of active and total connections both http and ws:
def conns_tracker(app_instance):
    async def tracker_middleware(scope, recv, send):

        if scope["type"] not in ("http","websocket"):
            await app_instance(scope,recv,send)
            return

        conn_type = scope["type"]
        state = scope.get("app").state

        if conn_type == "http":
            state.active_http +=1
            state.total_http+=1

        elif conn_type == "websocket":
            state.active_ws +=1
            state.total_ws+=1

        try:
            await app_instance(scope,recv,send)

        finally:
            if conn_type == "http":
                state.active_http -=1
                
            elif conn_type == "websocket":
                state.active_ws-=1
         
    return tracker_middleware



#heartbeats to eureka
async def server_health_check(state):
    health_status = {
        "service_name" :state.config.service_name,
        "Status" : "UP",
        "Database": "",
        "Cache" : ""
    }

    try:
        db_pool = getattr(state,"db_pool",None)
        if db_pool:
            async with asyncio.timeout(1):
                async with db_pool.acquire() as conn:
                    await conn.fetchval("SELECT 1;")
            health_status["Database"] = "UP"
        
        else:
            health_status["Database"] = "NONE"

    except Exception:
        health_status["Database"] = "DOWN"

    try:
        redis_client = getattr(state,"redis_client",None)
        if redis_client:
            async with asyncio.timeout(1):
                await redis_client.ping()

            health_status["Cache"] = "UP"
        else:
            health_status["Cache"] ="NONE"
    except Exception:
        health_status["Cache"] = "DOWN"

    if health_status["Database"] =="DOWN" or health_status["Cache"]=="DOWN":
        health_status["Status"] = "DOWN"

    return health_status


async def heartbeat_sender(app:FastAPI, heartbeat_interval:float =30):
    await asyncio.sleep(10)
    state =app.state
    while True:
        try:
                health_status = await server_health_check(state)

                client  = eureka_client.get_client()
                await client.status_update(health_status["Status"])

                await client.change_my_instance_metadata({
                                "active_requests": str(state.active_http + state.active_ws),
                                "Database": health_status["Database"],
                                "Cache": health_status["Cache"]
                            })

        except asyncio.CancelledError:
            break


        await asyncio.sleep(heartbeat_interval)



#monitoring route:

#returns server, database and cache health status
@monitor.get("/health")
async def server_health(req:Request):
    health_status =await  server_health_check(req.app.state)
   
    return health_status




#returns server metrics like uptime,start time, no. of requests handled, active requests
@monitor.get("/metrics")
async def server_metrics(req: Request):
    state = req.app.state
    uptime = time.time() - state.started_at
    metrics= {
        "service_name" :state.config.service_name,
        "start_time" : state.start_time_fmt,
        "uptime_sec" : uptime,
        "total_conn": state.total_http + state.total_ws,
        "total_http": state.total_http,
        "total_ws": state.total_ws,
        "total_active_conn": state.active_http + state.active_ws,
        "active_http" : state.active_http,
        "active_ws": state.active_ws
            
    }

    return metrics