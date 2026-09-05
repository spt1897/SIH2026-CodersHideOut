import asyncio
import redis.asyncio as redis

async def run_integration_test():
    # Connect to the Redis instance exposed by your Docker container
    r = redis.Redis(host='localhost', port=6379, db=0)
    
    print("--- PHASE 1: STACKING THE ZSET ---")
    # Priority Math Breakdown:
    # 385 -> Confirmed Landslide, Actual Score: 85 (Red) -> SHOULD DISPATCH
    # 260 -> AOT Projected, Actual Score: 60 (Orange) -> SHOULD DISPATCH
    # 135 -> Predicted, Actual Score: 35 (Yellow) -> NO DISPATCH (Dashboard only)
    # 15  -> Radius, Actual Score: 15 (Green) -> NO DISPATCH (Dashboard only)
    
    cells = {
        "cell_882a1072b59ffff": 385.0,
        "cell_882a1072b59fffe": 260.0,
        "cell_882a1072b59fffd": 135.0,
        "cell_882a1072b59fffc": 15.0
    }
    
    # Push the cells into the sorted set
    await r.zadd("cell_action_priority", cells)
    print(f"Loaded {len(cells)} cells into 'cell_action_priority'.")
    
    print("\n--- PHASE 2: FIRING THE TRIGGER ---")
    # Tell the microservice how many cells to pop
    await r.xadd("priority_cells_stream", {"no_of_cells": len(cells)})
    print("Trigger fired. Watching microservice reaction...\n")
    
    await asyncio.sleep(2) # Give the Docker container a second to process
    
    print("--- PHASE 3: THE COOLDOWN LOCK TEST ---")
    # Fire the exact same Confirmed Red cell again with a slightly different score
    await r.zadd("cell_action_priority", {"cell_882a1072b59ffff": 390.0})
    await r.xadd("priority_cells_stream", {"no_of_cells": 1})
    print("Duplicate critical cell fired.\n")
    
    await asyncio.sleep(1)

    print("--- PHASE 4: PUBLIC DASHBOARD VERIFICATION ---")
    # Verify that the service is actually routing data to the frontend stream
    dashboard_msgs = await r.xrange("dashboard_alerts_stream", min="-", max="+", count=10)
    for msg_id, payload in dashboard_msgs: # type: ignore
        decoded = {k.decode('utf-8'): v.decode('utf-8') for k, v in payload.items()} # type: ignore
        print(f"Frontend Received -> {decoded}")

    await r.aclose()

if __name__ == "__main__":
    asyncio.run(run_integration_test())