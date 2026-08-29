from pydantic import BaseModel

class Mapper(BaseModel):
    feature: str
    bbox : tuple[float, float,float, float]
    h3_res :int
