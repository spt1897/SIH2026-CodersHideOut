from pydantic import BaseModel

class Region(BaseModel):
    feature : str
    bbox : tuple[float, float, float, float]
    h3_res : int
    grid_res: float