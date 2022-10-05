from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class PredictionBase(BaseModel):
    image_url: Optional[HttpUrl]
    confidence: List[float]
    bounding_box: List[List[float]]
    healthiness: List[List[float]]


class PredictionCreate(PredictionBase):
    user_id: Optional[int]
    image_url: Optional[HttpUrl]
    confidence: List[float]
    bounding_box: List[List[float]]
    healthiness: List[List[float]]


class PredictionUpdate(PredictionBase):
    image_url: HttpUrl
    confidence: List[float]
    bounding_box: List[List[float]]
    healthiness: List[List[float]]


class PredictionInDBBase(PredictionBase):
    user_id: Optional[int]

    class Config:
        orm_mode = True


class Prediction(PredictionInDBBase):
    ...
