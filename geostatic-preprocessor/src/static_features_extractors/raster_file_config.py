import os

# Point BASE_DIR directly to static_features without os.path.dirname
BASE_DIR = r"D:\File-Storage\static_features"

RASTER_PATHS = {
    "elevation": os.path.join(BASE_DIR, r"DEM\processed\dem_elevation.tif"),
    "slope": os.path.join(BASE_DIR, r"DEM\processed\dem_slope.tiff"),
    "aspect": os.path.join(BASE_DIR, r"DEM\processed\dem_aspect.tiff"),
    "curvature": os.path.join(BASE_DIR, r"DEM\processed\dem_curvature.tiff"),
    "twi": os.path.join(BASE_DIR, r"DEM\processed\dem_twi.tiff"),
    "spi": os.path.join(BASE_DIR, r"DEM\processed\dem_spi.tiff"),
    "roughness": os.path.join(BASE_DIR, r"DEM\processed\dem_roughness.tiff"),
    "soil_type": os.path.join(BASE_DIR, r"soiltype\data\ne_india_soil_type.tif"),
    "ndvi_baseline": os.path.join(
        BASE_DIR, r"landcover\processed\ndvi_baseline.tif"
    ),
    "lulc": os.path.join(BASE_DIR, r"landcover\processed\lulc_mosaic.tif"),
}

SOIL_VRT_PATHS = {
    "sand": os.path.join(BASE_DIR, r"soiltype\data\sand_cropped.tif"),
    "silt": os.path.join(BASE_DIR, r"soiltype\data\silt_cropped.tif"),
    "clay": os.path.join(BASE_DIR, r"soiltype\data\clay_cropped.tif"),
}

GDB_PATH = os.path.join(BASE_DIR, r"lithology\data\LiMW_GIS 2015.gdb")

VECTOR_PATHS = {
    "roads": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\gis_osm_roads_free_1.shp"
    ),
    "railways": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\gis_osm_railways_free_1.shp"
    ),
    "rivers": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\gis_osm_waterways_free_1.shp"
    ),
    "waterways": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\gis_osm_waterways_free_1.shp"
    ),
    "powerlines": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\powerlines.geojson"
    ),
    "waterlines": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\waterlines.geojson"
    ),
    "telecom": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\telecom.geojson"
    ),
    "oillines": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\oillines.geojson"
    ),
    "faults": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\gem_active_faults.geojson"
    ),
    "buildings": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\gis_osm_buildings_a_free_1.shp"
    ),
    "water_bodies": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\gis_osm_water_a_free_1.shp"
    ),
    "pois": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\gis_osm_pois_free_1.shp"
    ),
    "pois_a": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\gis_osm_pois_a_free_1.shp"
    ),
    "traffic": os.path.join(
        BASE_DIR, r"openstreet-shapefile\data\gis_osm_traffic_free_1.shp"
    ),
    "states": os.path.join(BASE_DIR,r"openstreet-shapefile\data\india_states.shp")
}