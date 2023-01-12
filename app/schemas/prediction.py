from typing import Optional, List
from pydantic import BaseModel, HttpUrl

# Request
class PredictionCreateRequest(BaseModel):
    lat: float
    long: float


# Response
class PredictionResponseBase(BaseModel):
    user_id: Optional[int]


class OilPalmTree(BaseModel):
    user_id: int
    lat: float
    long: float
    nw_bounds: List[float]
    se_bounds: List[float]
    confidence: float

    class Config:
        orm_mode = True


class PredictionCreate(PredictionResponseBase):
    user_id: Optional[int]
    image_url: HttpUrl
    coco_bbox: List[List[float]]
    yolo_bbox: List[List[float]]
    confidence: List[float]
    trees: List[OilPalmTree]
    count: int

    class Config:
        orm_mode = True


class PredictionUpdate(PredictionResponseBase):
    image_url: HttpUrl
    confidence: List[float]
    coco_bbox: List[List[float]]
    yolo_bbox: List[List[float]]


class PredictionInDBBase(PredictionResponseBase):
    user_id: Optional[int]

    class Config:
        orm_mode = True


class Prediction(PredictionInDBBase):
    ...
