from datetime import datetime
from io import BytesIO
import requests

from PIL import Image
from typing import Any, List

from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response

from app import schemas, models, crud
from app.api import deps
from app.core.config import settings


router = APIRouter()


@router.get("/trees", status_code=200, response_model=List[schemas.OilPalmTree])
def get_predicted_trees(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    try:
        trees = crud.prediction.get_predicted_trees(db, user_id=current_user.id)
        for tree in trees:
            tree.created_at = str(tree.created_at)

        return trees
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.post("/predict", status_code=201, response_model=schemas.PredictionCreate)
def predict_image(
    *,
    db: Session = Depends(deps.get_db),
    request: schemas.PredictionCreateRequest,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:

    try:
        prediction, trees = crud.prediction.create(
            db, obj_in=request, user_id=current_user.id
        )
        resp_dict = {}
        resp_dict["user_id"] = prediction.user_id  # type: ignore
        resp_dict["yolo_bbox"] = prediction.yolo_bbox  # type: ignore
        resp_dict["confidence"] = prediction.confidence  # type: ignore
        resp_dict["coco_bbox"] = prediction.coco_bbox  # type: ignore
        resp_dict["count"] = prediction.count  # type: ignore
        resp_dict["image_url"] = prediction.image_url  # type: ignore
        resp_dict["trees"] = trees  # type: ignore
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    return resp_dict


@router.post("/image", responses={200: {"content": {"image/png": {}}}})
def get_image(
    *,
    request: schemas.PredictionCreateRequest,
    response_class=Response,
    current_user: models.User = Depends(deps.get_current_user),
):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={request.lat},{request.long}&zoom=20&scale=3&size=640x640&maptype=satellite&key={settings.MAP_API_KEY}"
    try:
        response = requests.get(url=url)
        img = BytesIO(response.content)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    return Response(content=img.getvalue(), media_type="image/png")
