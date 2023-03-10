from datetime import datetime
from io import BytesIO

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


@router.get(
    "/trees", status_code=status.HTTP_200_OK, response_model=List[schemas.OilPalmTree]
)
def get_predicted_trees(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    try:
        trees = crud.tree.get_all_trees(db, user_id=current_user.id)
        for tree in trees:
            tree.created_at = tree.created_at.strftime("%Y-%m-%d")

        return trees
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.delete("/trees/delete/{tree_id}", status_code=status.HTTP_200_OK)
def delete_tree_by_id(
    *,
    tree_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    try:
        crud.prediction.delete_tree(db, user_id=current_user.id, tree_id=tree_id)
        return {"message": f"Tree {tree_id} successfully deleted. {current_user.id}"}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.post(
    "/predict",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.PredictionCreate,
)
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
        prediction.trees = trees
        # print(prediction)
        # resp_dict = {}
        # resp_dict["user_id"] = prediction.user_id  # type: ignore
        # resp_dict["yolo_bbox"] = prediction.yolo_bbox  # type: ignore
        # resp_dict["confidence"] = prediction.confidence  # type: ignore
        # resp_dict["coco_bbox"] = prediction.coco_bbox  # type: ignore
        # resp_dict["count"] = prediction.count  # type: ignore
        # resp_dict["image_url"] = prediction.image_url  # type: ignore
        # for tree in trees:
        #     tree.created_at = tree.created_at.strftime("%Y-%m-%d")
        # resp_dict["trees"] = trees  # type: ignore
        # resp_dict["nw_bounds"] = prediction.nw_bounds
        # resp_dict["se_bounds"] = prediction.se_bounds
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    return prediction


@router.get(
    "/predictions",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.PredictionWithoutBox],
)
def get_predictions(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    try:
        predictions = crud.prediction.get_multi_by_user_id(db, user_id=current_user.id)
        for prediction in predictions:
            prediction.created_at = prediction.created_at.strftime("%Y-%m-%d")
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    return predictions


@router.get(
    "/total-trees",
    status_code=status.HTTP_200_OK,
    response_model=schemas.TotalOilPalmTree,
)
def get_total_trees(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
):
    try:
        total_trees = crud.prediction.get_total_trees(db, user_id=current_user.id)
        resp = TotalOilPalmTree()
        resp.total_trees = total_trees
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

    return resp


@router.get(
    "/predictions/{prediction_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.PredictionWithBox,
)
def get_prediction(
    *,
    prediction_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    try:
        prediction = crud.prediction.get_by_user_id(
            db, id=prediction_id, user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    return prediction


@router.post("/image", responses={status.HTTP_200_OK: {"content": {"image/png": {}}}})
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
