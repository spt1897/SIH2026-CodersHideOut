from src.service.gis_service.get_cell_data import *
from src.service.gis_service.get_metric_data import *
import time

mertric_function_mapping ={
    "elevation" : get_elevation_feature_collection,
    "slope" : get_slope_feature_collection,
    "twi" : get_twi_feature_collection,
    "spi" : get_spi_feature_collection,
    "vegetation" :get_vegetation_feature_collection,
    "building density": get_building_density_feature_collection,
    "road density": get_road_density_feature_collection,
    "drainage density": get_drainage_density_feature_collection

}

async def gis_service(req,app):
    match req["request"]:
        case "cell_data":
            data = await get_cell_data(req["h3_index"],app)
            json_response={
                "metadata": {
                    "type" : "requested_data",
                    "category": "cell_data",
                    "timestamp": time.time()
                },
                "data": data
            }

            return json_response

        case _:
            data = mertric_function_mapping[req["request"]]()
            json_response={
                            "metadata": {
                                "type" : "requested_data",
                                "category": req["request"],
                                "timestamp": time.time()
                            },
                            "data": data
                        }
            return json_response

        