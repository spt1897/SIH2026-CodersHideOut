import redis.asyncio as redis
import asyncpg
from src.core.db_redis_manager.db_query_handler import query_db
from src.core.db_redis_manager.redis_query_handler import query_redis
import asyncio
import aiohttp
import h3
from src.service.calc_priority import calc_priority

RADIUS =1

async def process(msg,app,service_name):
    config = app.state.config
    prioritized_list  = []
    cell_ids= []
    cell_probs = []
    cell_types = []
    msg_ids_1 = []
    msg_ids_2 = []
    msg_ids_3 = []
    unique_radius_cells =set()
    for stream, entries in msg:
        for msg_id,data in entries:
            if stream =="predicted_landslide_cells":
                cell_types.append("predicted")
                msg_ids_1.append(msg_id)
                cell_probs.append(data.pop("landslide_probability"))

                source_lat, source_lon = h3.cell_to_latlng(data["h3_index"])
                radius_cells = h3.grid_disk(data["h3_index"], 45)

                for cell in radius_cells:

                    lat, lon = h3.cell_to_latlng(cell)

                    distance_km = h3.great_circle_distance(
                        (source_lat, source_lon),
                        (lat, lon),
                        unit="km"
                    )

                    if distance_km <= RADIUS:
                        unique_radius_cells.add(cell)
                    
                
            elif stream =="confirmed_landslide_cells":
                cell_types.append("confirmed")
                msg_ids_2.append(msg_id)
                cell_probs.append(None)
            elif stream =="projected_landslide_cells":
                cell_types.append("projected")
                msg_ids_3.append(msg_id)
                cell_probs.append(None)

            cell_ids.append(data.pop("h3_index"))
            

    cell_set = set(cell_ids)
    for cell in unique_radius_cells:
        if cell not in cell_set:
            cell_ids.append(cell)
            cell_types.append("radius_cells")
            cell_probs.append(None)

    async def getcelldata(conn:asyncpg.Connection):
        return await conn.fetch("""SELECT
                                    c.h3_index,
                                    c.is_farmland,
                                    c.has_NH,
                                    c.has_SH,
                                    c.population_density,
                                    c.building_density,
                                    c.road_density,
                                    c.railway_density,
                                    cardinality(c.powerline_ids) AS powerlines,
                                    cardinality(c.waterline_ids) AS waterlines,
                                    cardinality(c.telecom_ids) AS telecoms,
                                    cardinality(c.oilline_ids) AS oillines
                                FROM unnest($1::text[]) WITH ORDINALITY AS u(h3_index, ord)
                                JOIN cell_landmark_mapping c USING (h3_index)
                                ORDER BY u.ord;""",cell_ids)


    async def gettrafficdata(lat,long):
            params = {
                "key": config.tomtom_api_key,
                "point": f"{lat},{long}",
                "unit": "KMPH"
            }

            async with session.get("https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json",params=params) as res:
                if res.status!=200:
                    return None
                return await res.json()["flowSegmentData"]


    celldatas = await query_db(getcelldata,app)

    tasks = []
       
    async with aiohttp.ClientSession() as session:
        for cell in cell_ids:
            lat,long = h3.cell_to_latlng(cell)
            tasks.append(gettrafficdata(lat,long))

        traffic_datas = await asyncio.gather(*tasks,return_exceptions=True)


    prioritized_list = await calc_priority(cell_ids,cell_probs,cell_types,celldatas,traffic_datas)

    async def push_priorities(redis_client:redis.Redis):
        pipe = redis_client.pipeline()
        for cell,priority in zip(cell_ids,prioritized_list):
            pipe.zadd("cell_action_priority",{cell: priority})

        pipe.xadd("priority_cells_stream",{"number_of_cells":len(cell_ids)})
        await pipe.execute()


    async def ack(redis_client:redis.Redis):
        await redis_client.xack("predicted_landslide_cells",service_name,*msg_ids_1)
        await redis_client.xack("confirmed_landslide_cells",service_name,*msg_ids_2)
        await redis_client.xack("projected_landslide_cells",service_name,*msg_ids_3)

    await query_redis(push_priorities,app)
    await query_redis(ack,app)