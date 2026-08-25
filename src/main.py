'''Sample main function setup for microservice'''
from fastapi import FastAPI
import uvicorn
from src.core.server_manager.server_lifespan import lifespan
from src.core.server_manager.server_monitor_router import monitor
from src.core.server_manager.server_monitor_router import conns_tracker
from src.core.server_manager.get_server_ip import get_server_ip

from test import test

app = FastAPI(title="translation-service",lifespan=lifespan())


#Routers:
app.include_router(monitor)
app.include_router(test) # test1
#Middlewares:
#asgi wrapper middlewares:
app.add_middleware(conns_tracker)


def main():
    uvicorn.run("src.main:app" ,host=get_server_ip(),port=8080 ,reload=True)
    pass

if __name__ == '__main__':
    main()