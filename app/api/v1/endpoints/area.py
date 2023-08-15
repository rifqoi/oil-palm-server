from datetime import datetime
from io import BytesIO

from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature
import geojson

import requests

from PIL import Image
from typing import Any, List

from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, responses, status
from fastapi import Response

from app import schemas, models, crud
from app.api import deps
from app.core.config import settings
from app.schemas.prediction import TotalOilPalmTree


router = APIRouter()


def string_to_geojson(jsonstr: str):
    try:
        geojson_dict = geojson.loads(jsonstr)
    except Exception as e:
        raise e

    return geojson_dict


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.AreaGet])
def get_all_areas(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    try:
        areas = crud.area.get_areas(db, user_id=current_user.id)
        trees = crud.tree.get_all_trees_center(db, user_id=current_user.id)
        for area in areas:
            geojson_dict = string_to_geojson(area.geojson)

            tree_in_area = []
            for tree in trees:
                point = Feature(geometry=Point(tree))
                polygon = Polygon(geojson_dict["geometry"]["coordinates"])
                res = boolean_point_in_polygon(point, polygon)
                if res:
                    tree_in_area.append(tree)

            area.total_trees = len(tree_in_area)
            area.geojson = geojson_dict

        return areas
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.post("/", status_code=status.HTTP_200_OK)
def insert_area(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    obj_in: schemas.AreaInsert,
):
    try:
        area = crud.area.add_area(db, user_id=current_user.id, obj_in=obj_in)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    return {"message": "Area inserted!"}
