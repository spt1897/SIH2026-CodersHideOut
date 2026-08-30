import xgboost as xgb
from src.landslide_predictor.state import model

def init_model():
    global model
    model = xgb.Booster()
    model.load_model("./XGBoost_Landslide_Model.json")