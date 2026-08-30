from src.synchronizer.sync_db_with_cache import *

async def start_syncers(app):
    app.state.syncer1= asyncio.create_task(sync_db_with_predictions(app))
    app.state.syncer2 = asyncio.create_task(sync_db_with_realtime_data(app))


async def stop_syncers(app):
    app.state.syncer1.cancel()
    app.state.syncer2.cancel()