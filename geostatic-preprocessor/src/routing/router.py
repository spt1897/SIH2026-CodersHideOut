from fastapi import FastAPI, APIRouter
from src.static_features_extractors.coord_to_h3_aggregate import *
from src.static_features_extractors.distance_extractors import *
from src.static_features_extractors.lithology_extractors import *
from src.static_features_extractors.soiltexture_extractor import *
from src.static_features_extractors.terrain_feature_extractor import *
from src.geo_features_processors.cell_landmark_mapper import *
from src.geo_features_processors.emergency_nodes_extractor import *


extractor = APIRouter(prefix="/extract")

extractor.post("/static-features/")