import numpy as np
import xgboost as xgb
from src.landslide_predictor.state import model

def predict(feature_vector_batch: list[list]):
    global model
    X = np.asarray(feature_vector_batch,dtype=np.float32)

    probabilities =  model.predict(xgb.DMatrix(X))

    return probabilities.tolist()

