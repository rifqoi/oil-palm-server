from datetime import datetime
from io import BytesIO
from turfpy.measurement import boolean_point_in_polygon
from geojson import Point, Polygon, Feature

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

        jsn = {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [107.02655, -6.472885],
                        [107.025279, -6.471629],
                        [107.027918, -6.468141],
                        [107.027532, -6.468258],
                        [107.02721, -6.468301],
                        [107.02691, -6.468557],
                        [107.026684, -6.468578],
                        [107.026716, -6.468952],
                        [107.026674, -6.46924],
                        [107.026521, -6.469308],
                        [107.026475, -6.469183],
                        [107.026566, -6.469097],
                        [107.026531, -6.468945],
                        [107.026314, -6.468713],
                        [107.026022, -6.468439],
                        [107.02545, -6.468281],
                        [107.024981, -6.468148],
                        [107.024646, -6.468196],
                        [107.024592, -6.468476],
                        [107.024957, -6.468649],
                        [107.025163, -6.468852],
                        [107.025228, -6.469073],
                        [107.025231, -6.469287],
                        [107.025169, -6.469111],
                        [107.025056, -6.469036],
                        [107.024968, -6.46906],
                        [107.02497, -6.468921],
                        [107.024823, -6.468785],
                        [107.024536, -6.468655],
                        [107.02441, -6.468887],
                        [107.024125, -6.46966],
                        [107.023822, -6.470353],
                        [107.02272, -6.470209],
                        [107.021787, -6.47022],
                        [107.021835, -6.470935],
                        [107.021931, -6.471265],
                        [107.022232, -6.471777],
                        [107.02338, -6.471409],
                        [107.023578, -6.471457],
                        [107.023889, -6.47166],
                        [107.024485, -6.471846],
                        [107.02486, -6.472054],
                        [107.02655, -6.472885],
                    ]
                ],
            },
        }

        trees2 = crud.tree.get_all_trees_center(db, user_id=current_user.id)
        tree_in_area = []
        for tree in trees2:
            point = Feature(geometry=Point(tree))
            polygon = Polygon(jsn["geometry"]["coordinates"])
            res = boolean_point_in_polygon(point, polygon)
            if res:
                tree_in_area.append(tree)
            print(res)
        print(len(tree_in_area))
        print(tree_in_area)
        return trees
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.put(
    "/trees/edit/{tree_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.OilPalmTree,
)
def update_tree_by_id(
    *,
    tree_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    obj_in: schemas.TreeUpdateRequest,
):
    try:
        updated_tree = crud.tree.update_tree_status(
            db, user_id=current_user.id, tree_id=tree_id, obj_in=obj_in
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    return updated_tree


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
        print(prediction)
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
