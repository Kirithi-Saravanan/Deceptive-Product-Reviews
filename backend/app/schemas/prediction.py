from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PredictionCreate(BaseModel):
    product_name: str
    rating: int
    review_title: str
    review_text: str

class PredictionResponse(PredictionCreate):
    id: int
    user_id: int
    predicted_class: int
    predicted_label: str
    probability_deceptive: Optional[float]
    probability_genuine: Optional[float]
    threshold_used: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
