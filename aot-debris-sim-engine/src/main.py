from fastapi import FastAPI
import uvicorn
from src.core.server_manager.server_lifespan import lifespan
from src.core.server_manager.server_monitor_router import monitor
from src.core.server_manager.server_monitor_router import conns_tracker
from src.core.server_manager.get_server_ip import get_server_ip


app = FastAPI(title="translation-service",lifespan=lifespan())





async def main():
    pass

if __name__ == '__main__':
    main()