from typing import Optional, List, Tuple
from io import BytesIO

import numpy as np
import requests
from sqlalchemy.orm import Session
from PIL import Image

from app.crud.base import CRUDBase
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate, PredictionUpdate, PredictionCreateRequest
from app.core.config import settings
from app.ml_inference.yolo import OilPalmModel, BoundingBox

def read_image_from_url(url: str) -> np.array:
    response = requests.get(url=url)
    img = Image.open(BytesIO(response.content))

    arr = np.asarray(img)
    return arr

def static_map_url(lat: float, long:float, zoom: int, width: int, height: int,) -> Tuple[str, str]:
    url_without_key = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom={zoom}&scale=3&size={width}x{height}&maptype=satellite&key="
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom={zoom}&scale=3&size={width}x{height}&maptype=satellite&key={settings.MAP_API_KEY}"
    return url, url_without_key

def convert_yolo_to_coco(yolo_bboxes: List[BoundingBox], img_width: int, img_height: int) -> List[BoundingBox]:
    coco_bboxes: List[BoundingBox] = []
    for yolo_bbox in yolo_bboxes:
        coco_bbox = BoundingBox()

        coco_width = yolo_bbox.width * img_width
        coco_height = yolo_bbox.height * img_height
        coco_x = yolo_bbox.x * img_width - (coco_width / 2)
        coco_y = yolo_bbox.y * img_height - (coco_height / 2)

        coco_bbox.x = coco_x
        coco_bbox.y = coco_y
        coco_bbox.width = coco_width
        coco_bbox.height = coco_height
        coco_bbox.label = yolo_bbox.label
        coco_bbox.confidence = yolo_bbox.confidence

        coco_bboxes.append(coco_bbox)

    return coco_bboxes

def bbox_to_array(bboxes: List[BoundingBox]) -> List[List[float]]:
    array: List[List[float]] = []
    for bbox in bboxes:
        box_array: List[float] = []

        box_array.append(bbox.x)
        box_array.append(bbox.y)
        box_array.append(bbox.width)
        box_array.append(bbox.height)

        array.append(box_array)

    return array

def bbox_to_confidence(bboxes: List[BoundingBox]) -> List[float]:
    conf_array: List[float] = []

    for bbox in bboxes:
        conf_array.append(bbox.confidence)

    return conf_array


class CRUDPrediction(CRUDBase[Prediction, PredictionCreate, PredictionUpdate]):
    def create(self, db: Session, *, obj_in: PredictionCreateRequest, user_id: int) -> Optional[Prediction]:
        model = OilPalmModel()
        width = 640
        height = 640
        url, url_without_key = static_map_url(obj_in.lat, obj_in.long, 20, width=width, height=height)
        img_array = read_image_from_url(url)
        yolo_bbox = model.predict(img_array)
        coco_bbox = convert_yolo_to_coco(yolo_bbox, width, height)

        yolo_array = bbox_to_array(yolo_bbox)
        coco_array = bbox_to_array(coco_bbox)
        conf_array = bbox_to_confidence(yolo_bbox)
        count = len(yolo_array)

        db_obj = Prediction()
        db_obj.user_id = user_id
        db_obj.yolo_bbox = yolo_array
        db_obj.coco_bbox = coco_array
        db_obj.confidence = conf_array
        db_obj.image_url = url_without_key
        db_obj.count = count

        db.add(db_obj)
        db.commit()

        return db_obj

prediction = CRUDPrediction(Prediction)
