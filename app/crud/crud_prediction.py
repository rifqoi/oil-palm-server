from typing import Optional, List, Tuple
from io import BytesIO

import numpy as np
import requests
from sqlalchemy.orm import Session, query
from PIL import Image

from app.crud.base import CRUDBase
from app.mercator.google_static_maps import GoogleStaticMap
from app.mercator.mercator_projection import G_LatLng
from app.ml_inference.yolo7 import OilPalmModelYoloV7
from app.models.prediction import Prediction
from app.models.tree import Tree
from app.schemas.prediction import (
    PredictionCreate,
    PredictionUpdate,
    PredictionCreateRequest,
)
from app.core.config import settings
from app.ml_inference.yolo4 import OilPalmModel, BoundingBox


def read_image_from_url(url: str) -> np.ndarray:
    response = requests.get(url=url)
    img = Image.open(BytesIO(response.content))

    arr = np.asarray(img)
    return arr


def static_map_url(
    lat: float,
    long: float,
    zoom: int,
    width: int,
    height: int,
) -> Tuple[str, str]:
    url_without_key = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom={zoom}&scale=3&size={width}x{height}&maptype=satellite&key="
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom={zoom}&scale=3&size={width}x{height}&maptype=satellite&key={settings.MAP_API_KEY}"
    return url, url_without_key


def convert_yolo_to_coco(
    yolo_bboxes: List[BoundingBox], img_width: int, img_height: int
) -> List[BoundingBox]:
    coco_bboxes: List[BoundingBox] = []
    for yolo_bbox in yolo_bboxes:
        coco_bbox = BoundingBox()

        x = yolo_bbox.x * img_width
        y = yolo_bbox.y * img_height

        x2 = yolo_bbox.width * img_width
        y2 = yolo_bbox.height * img_height

        w = x2 - x
        h = y2 - y

        x_center = x + w / 2
        y_center = y + h / 2
        coco_bbox.x = x
        coco_bbox.y = y
        coco_bbox.width = w
        coco_bbox.height = h
        coco_bbox.label = yolo_bbox.label
        coco_bbox.confidence = yolo_bbox.confidence
        coco_bbox.x_center = x_center
        coco_bbox.y_center = y_center

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


class CRUDPrediction:
    def get_predicted_trees(self, db: Session, *, user_id: int):
        trees = db.query(Tree).filter(Tree.user_id == user_id).all()
        return trees

    def delete_tree(self, db: Session, *, user_id: int, tree_id: int):
        rows_affected = (
            db.query(Tree)
            .filter(Tree.tree_id == tree_id and Tree.user_id == user_id)
            .delete()
        )
        if rows_affected == 0:
            raise Exception(f"Tree with id {tree_id} not found")

        db.commit()

    def get_multi_by_user_id(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 5000
    ) -> List[Prediction]:
        return (
            db.query(Prediction)
            .filter(Prediction.user_id == user_id)
            .order_by(Prediction.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_id(
        self, db: Session, *, id: int, user_id: int
    ) -> Optional[Prediction]:
        return (
            db.query(Prediction)
            .filter(Prediction.user_id == user_id)
            .filter(Prediction.id == id)
            .first()
        )

    def get_total_trees(self, db: Session, *, user_id: int) -> Optional[int]:
        return db.query(Tree).filter(Tree.user_id == user_id).count()

    def create(
        self, db: Session, *, obj_in: PredictionCreateRequest, user_id: int
    ) -> Tuple[Prediction, List[Tree]]:
        height = 640
        width = 640
        center = G_LatLng(
            obj_in.lat,
            obj_in.long,
        )

        model = OilPalmModel()
        map = GoogleStaticMap(width, height)
        url, url_without_key = map.static_map_url(
            obj_in.lat,
            obj_in.long,
            20,
        )
        img_array = map.read_image_from_url(url)
        yolo_bbox = model.predict(img_array)
        coco_bbox = convert_yolo_to_coco(yolo_bbox, width, height)

        yolo_array = bbox_to_array(yolo_bbox)
        count = len(yolo_array)

        last_pred = (
            db.query(Prediction)
            .filter(Prediction.user_id == user_id)
            .order_by(Prediction.prediction_id.desc())
            .first()
        )
        pred_id = None
        if isinstance(last_pred, Prediction):
            if last_pred.prediction_id:
                pred_id = last_pred.prediction_id + 1
        else:
            pred_id = 1

        pred_obj = Prediction(
            user_id=user_id,
            image_url=url_without_key,
            center_coords=[obj_in.lat, obj_in.long],
            nw_bounds=obj_in.nw_bounds,
            se_bounds=obj_in.se_bounds,
            prediction_id=pred_id,
            count=count,
        )

        trees: List[Tree] = []
        last_tree = (
            db.query(Tree)
            .filter(Tree.user_id == user_id)
            .order_by(Tree.tree_id.desc())
            .first()
        )

        last_id = None
        if isinstance(last_tree, Tree):
            last_id = last_tree.tree_id

        count = 1
        for bbox in coco_bbox:
            latlng = map.get_lat_long(center, 20, bbox.x_center, bbox.y_center)
            bound = map.get_bounds_lat_long(
                center, 20, bbox.x, bbox.y, bbox.width, bbox.height
            )
            if isinstance(last_id, int):
                last_id += 1
            else:
                last_id = 1

            # if count == 1:
            #     print("yolo", yolo_bbox[0])
            #     print("coco", bbox)
            #     print("lat", latlng.lat)
            #     print("lng", latlng.lng)
            #     print()

            tree_obj = Tree(
                user_id=user_id,
                tree_id=last_id,
                lat=latlng.lat,
                long=latlng.lng,
                nw_bounds=[bound.nw.lat, bound.nw.lng],
                se_bounds=[bound.se.lat, bound.se.lng],
                confidence=bbox.confidence,
                coco_bbox=bbox,
                prediction=pred_obj,
            )
            trees.append(tree_obj)
            db.add(tree_obj)
            db.commit()

        return pred_obj, trees


prediction = CRUDPrediction()
