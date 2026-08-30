from pydantic import BaseModel

class H3_Prediction(BaseModel):
    h3_index:str
    landslide_probability :float