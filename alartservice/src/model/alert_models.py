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

class ProcessedAlert(BaseModel):
    cell_id: str
    cell_type: str       # Confirmed, AOT, Predicted, or Radius
    raw_priority: float  # The original 0-400 score
    actual_score: float  # The 0-100 normalized score
    alert_color: str     # Red, Orange, Yellow, Green