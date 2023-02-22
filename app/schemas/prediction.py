from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, HttpUrl

# Request
class PredictionCreateRequest(BaseModel):
    lat: float
    long: float
    nw_bounds: List[float]
    se_bounds: List[float]


# Response
class PredictionResponseBase(BaseModel):
    user_id: Optional[int]


class OilPalmTree(BaseModel):
    id: int
    user_id: int
    tree_id: int
    lat: float
    long: float
    nw_bounds: List[float]
    se_bounds: List[float]
    confidence: float
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True


class TotalOilPalmTree(BaseModel):
    total_trees: Optional[int]


class PredictionCreate(PredictionResponseBase):
    user_id: Optional[int]
    count: int
    nw_bounds: List[float]
    se_bounds: List[float]
    image_url: HttpUrl
    coco_bbox: List[List[float]]
    yolo_bbox: List[List[float]]
    confidence: List[float]
    trees: List[OilPalmTree]

    class Config:
        orm_mode = True


class PredictionUpdate(PredictionResponseBase):
    image_url: HttpUrl
    confidence: List[float]
    coco_bbox: List[List[float]]
    yolo_bbox: List[List[float]]


class PredictionWithoutBox(BaseModel):
    id: Optional[int]
    prediction_id: Optional[int]
    user_id: Optional[int]
    count: Optional[int]
    nw_bounds: Optional[List[float]]
    se_bounds: Optional[List[float]]
    center_coords: Optional[List[float]]
    created_at: Optional[str]

    class Config:
        orm_mode = True


class PredictionInDBBase(PredictionResponseBase):
    user_id: Optional[int]

    class Config:
        orm_mode = True


class Prediction(PredictionInDBBase):

    ...
