from pydantic import BaseModel
class TopicAlert(BaseModel):
    topic: str
    title: str
    body: str
    severity: str

class TokenAlert(BaseModel):
    token: str
    title: str
    body: str
    severity: str

class LandslideAlert(BaseModel):
    title: str
    latitude: float
    longitude: float
    danger_radius_in_hexagons: int = 1
    body: str
    severity: str

class SubscriptionRequest(BaseModel):
    token: str
    topic: str