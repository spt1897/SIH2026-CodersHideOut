from fastapi import FastAPI
import uvicorn
from src.core.server_manager.server_lifespan import lifespan
from src.core.server_manager.get_server_ip import get_server_ip



app = FastAPI(title="translation-service",lifespan=lifespan())

#routing is used to control Pre-processing stage:
# 1) Files downloader/updater
# 2) Geo-spatial indexing (mapping villages,cities,localities to H3 cells)
# 3) Calculate static terrain features for each H3 cell
# 4) Do it all together

def main():
    uvicorn.run("src.main:app" ,host=get_server_ip(),port=8080 ,reload=True)
    pass

if __name__ == '__main__':
    main()