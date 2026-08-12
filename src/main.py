'''Sample main function setup for microservice'''
from fastapi import FastAPI
import uvicorn
from src.core.server_manager.server_lifespan import lifespan
from src.core.server_manager.server_monitor_router import monitor
from src.core.server_manager.server_monitor_router import conns_tracker

app = FastAPI(title="translation-service",lifespan=lifespan)

#Routers:
app.include_router(monitor)

#Middlewares:
#asgi wrapper middlewares:
app.router = conns_tracker(app_instance=app.router)


def main():
    uvicorn.run("src.main:app" ,host='0.0.0.0',port=8080 ,reload=True)
    pass

if __name__ == '__main__':
    main()