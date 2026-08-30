from fastapi import FastAPI
from concurrent.futures import ProcessPoolExecutor
import time
from typing import Callable
'''
This module initializes necessary appstate variables
'''
async def init_appstate(app:FastAPI,process_pool_init:Callable,args:tuple[()]):
    #store server start time
    app.state.started_at = time.time()
    app.state.start_time_fmt = time.strftime("%Y-%m-%d %H:%M:%S UTC",time.gmtime(app.state.started_at))
    #num of conn trackers
    app.state.active_http =0
    app.state.active_ws = 0
    app.state.total_http = 0
    app.state.total_ws = 0
    #initialize process pool for cpu heavy tasks
    config =app.state.config
    if hasattr(config,"process_pool_size") and config.process_pool_size>0:
        app.state.process_pool = ProcessPoolExecutor(
                            max_workers=config.process_pool_size,
                            initializer=process_pool_init,
                            initargs=args)