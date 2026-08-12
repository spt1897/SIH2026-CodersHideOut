from fastapi import FastAPI
import time
'''
This module initializes necessary appstate variables
'''
async def init_appstate(app:FastAPI):
    #store server start time
    app.state.started_at = time.time()
    app.state.start_time_fmt = time.strftime("%Y-%m-%d %H:%M:%S UTC",time.gmtime(app.state.started_at))
    #num of conn trackers
    app.state.active_http =0
    app.state.active_ws = 0
    app.state.total_http = 0
    app.state.total_ws = 0