from src.core.db_redis_manager.redis_query_handler import *
from src.core.db_redis_manager.db_query_handler import *
import asyncpg
async def get_cell_data(h3_index,app):
    async def get_data(conn:asyncpg.Connection):
        return await conn.fetch("""SELECT t1.*,t3.police_names,t3.hospital_names,t3.fire_names,t3.traffic_booth_names,
                                    t2.state_names,
                                    t2.district_names,
                                    t2.sub_districts,
                                    t2.cities_towns,
                                    t2.localities_villages,

                                    cardinality(t2.road_ids)      AS number_of_roads,
                                    cardinality(t2.railway_ids)   AS number_of_railways,
                                    cardinality(t2.river_ids)     AS number_of_rivers,
                                    cardinality(t2.powerline_ids) AS number_of_powerlines,
                                    cardinality(t2.waterline_ids) AS number_of_waterlines,
                                    cardinality(t2.telecom_ids)   AS number_of_telecom_lines,
                                    cardinality(t2.oilline_ids)   AS number_of_oil_lines,

                                    t2.is_farmland,
                                    t2.has_NH,
                                    t2.has_SH,
                                    t2.population_density,
                                    t2.estimated_population,
                                    t2.building_density,
                                    t2.road_density,
                                    t2.railway_density,
                                    t2.landmark_names
                                    from prediction_parameters t1 JOIN cell_landmark_mapping t2 ON t1.h3_index = t2.h3_index JOIN cell_emergency_nodes t3 ON t2.h3_index =t3.h3_index WHERE t1.h3_index=$1""", h3_index)

    return dict((await query_db(get_data,app))[0])