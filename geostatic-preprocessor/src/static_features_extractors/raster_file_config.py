import os

BASE_DIR = os.path.dirname(r"D:\File-Storage\static_features")


RASTER_PATHS = {
"elevation": os.path.join(BASE_DIR, "dem/processed/dem_elevation.tiff"),
"slope": os.path.join(BASE_DIR, "dem/processed/dem_slope.tiff"),
"aspect": os.path.join(BASE_DIR, "dem/processed/dem_aspect.tiff"),
"curvature": os.path.join(BASE_DIR, "dem/processed/dem_curvature.tiff"),
"twi": os.path.join(BASE_DIR, "dem/processed/dem_twi.tiff"),
"spi": os.path.join(BASE_DIR, "dem/processed/dem_spi.tiff"),
"roughness": os.path.join(BASE_DIR, "dem/processed/dem_roughness.tiff"),
"soil_type": os.path.join(BASE_DIR, "soiltype/data/ne_india_soil_type.tif"),
"ndvi_baseline": os.path.join(
BASE_DIR, "landcover/processed/ndvi_baseline.tiff"
),
"lulc": os.path.join(BASE_DIR, "landcover/processed/lulc_mosaic.tiff"),
}

SOIL_VRT_PATHS = {
"sand": os.path.join(BASE_DIR, "soiltype/data/sand_0-5cm_mean.vrt"),
"silt": os.path.join(BASE_DIR, "soiltype/data/silt_0-5cm_mean.vrt"),
"clay": os.path.join(BASE_DIR, "soiltype/data/clay_0-5cm_mean.vrt"),
}

GDB_PATH = os.path.join(BASE_DIR, "lithology/data/LiMW_GIS 2015.gdb")

VECTOR_PATHS = {
"faults": os.path.join(
    BASE_DIR, "openstreet-shapefile/data/gem_active_faults.geojson"
),
"roads": os.path.join(
    BASE_DIR, "openstreet-shapefile/data/gis_osm_roads_free_1.shp"
),
"buildings": os.path.join(
    BASE_DIR, "openstreet-shapefile/data/gis_osm_buildings_a_free_1.shp"
),
"waterways": os.path.join(
    BASE_DIR, "openstreet-shapefile/data/gis_osm_waterways_free_1.shp"
),
"water_bodies": os.path.join(
    BASE_DIR, "openstreet-shapefile/data/gis_osm_water_a_free_1.shp"
),
}