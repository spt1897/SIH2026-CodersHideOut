from fastapi import FastAPI, APIRouter, Request,HTTPException
from src.static_features_extractors.coord_to_h3_aggregate import *
from src.static_features_extractors.distance_extractors import *
from src.static_features_extractors.lithology_extractors import *
from src.static_features_extractors.soiltexture_extractor import *
from src.static_features_extractors.terrain_feature_extractor import *
from src.geo_features_processors.cell_landmark_mapper import *
from src.geo_features_processors.emergency_nodes_extractor import *
from src.geo_features_processors.infra_extractor import *
from src.models.extract_static_features import *
from src.core.db_redis_manager.db_query_handler import query_db
import asyncio
from functools import partial
import asyncpg
from src.models.mapper import *

extractor = APIRouter(prefix="/extract")

@extractor.post("/static-features/")
async def extract_static_feature(region : Region, req : Request):
    process_pool = req.app.state.process_pool
    loop = asyncio.get_running_loop()
    match region.feature:
        case "elevation_m":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_elevation_batch))
        case "slope_deg":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_slope_batch))
        case "aspect_deg":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_aspect_batch))
        case "curvature":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_curvature_batch))
        case "twi":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_twi_batch))
        case "spi":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_spi_batch))
        case "roughness":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_roughness_batch))

        # --- Lithology ---
        case "lithology_encoded":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_lithology_batch))

        # --- Soil type (ISRIC) ---
        case "soil_type":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_soil_type_batch))
        case "soil_texture":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_soil_texture_batch))

        # --- OpenStreetMap (OSM) ---
        case "distance_to_fault_m":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_distance_to_fault_batch))
        case "distance_to_road_m":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_distance_to_road_batch))
        case "distance_to_river_m":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_distance_to_river_batch))
        case "drainage_density":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_drainage_density_batch))
        case "building_density":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_building_density_batch))

        # --- Landcover (ESA WorldCover) ---
        case "ndvi_baseline":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_ndvi_baseline_batch))
        case "lulc":
            tuple_data,query = await loop.run_in_executor(process_pool, partial(coord_to_h3_aggregate, bbox = region.bbox,
                                                                          grid_resolution_deg=region.grid_res,
                                                                          parameter_name=region.feature, h3_resolution=region.h3_res, 
                                                                          extractor_func= get_lulc_batch))

        # --- Default ---
        case _:
            return {"Status": f"Unknown feature: '{region.feature}'"}

    async def db_upsert(conn: asyncpg.Connection) -> int:
        if not tuple_data:
            return 0
        await conn.executemany(query, tuple_data)
        return len(tuple_data)

    await query_db(query_func=db_upsert,app=req.app)
    return {"data" : tuple_data}
    return {"Status": f"{region.feature} extracted and upserted to Database for Region: {region.bbox} successfully."}



@extractor.post("/geo-features")
async def extract_geo_features(mapper: Mapper, req: Request):
    loop =asyncio.get_running_loop()
    pool = req.app.state.process_pool

    if mapper.feature == "emergency":
        res = await loop.run_in_executor(pool,extract_emergency_nodes,mapper.bbox,mapper.h3_res)

    elif mapper.feature == "cell_landmarks":
        res = await loop.run_in_executor(pool,cell_landmark_mapper,mapper.bbox,mapper.h3_res)
    
    elif mapper.feature == "infrastructure":
        res = await loop.run_in_executor(pool,fetch_infrastructure_by_bbox,mapper.bbox,mapper.h3_res)
 

    return {"data": res["records"]}