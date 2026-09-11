import asyncpg
from src.core.db_redis_manager.db_query_handler import *
import time

async def get_affected_roads(
    h3_indexes: list[str],
    cell_types: list[str],
    app
):

    async def get_data(conn: asyncpg.Connection):
        row = await conn.fetchrow(
            """
            WITH input_cells AS (
                SELECT *
                FROM unnest($1::text[], $2::text[])
                     AS t(h3_index, cell_type)
            ),

            road_features AS (
                SELECT DISTINCT ON (r.road_id)
                    r.road_id,
                    r.name,
                    r.geom,

                    CASE ic.cell_type
                        WHEN 'Confirmed Landslide'    THEN '#FF0000'
                        WHEN 'AOT Projected'   THEN '#FF8C00'
                        WHEN 'Predicted Landslide'  THEN '#FFD700'
                        WHEN '1km Radius of Predicted' THEN '#3B82F6'
                        ELSE '#808080'
                    END AS color

                FROM input_cells ic
                JOIN cell_landmark_mapping clm
                    ON clm.h3_index = ic.h3_index
                JOIN roads r
                    ON r.road_id = ANY(clm.road_ids)
            )

            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features',
                COALESCE(
                    json_agg(
                        json_build_object(
                            'type', 'Feature',
                            'id', road_id,
                            'geometry',
                                ST_AsGeoJSON(
                                    ST_Transform(geom, 4326)
                                )::json,
                            'properties',
                                json_build_object(
                                    'road_id', road_id,
                                    'name', name,
                                    'color', color
                                )
                        )
                    ),
                    '[]'::json
                )
            ) AS geojson
            FROM road_features;
            """,
            h3_indexes,
            cell_types
        )

        return row["geojson"]

    data = await query_db(get_data, app)

    json_data = {}
    json_data["metadata"] = {"type" : "broadcast", "category": "affected_roads", "data_items" :1}
    json_data["data"] = data
    json_data["metadata"]["timestamp"] = time.time()

    return json_data