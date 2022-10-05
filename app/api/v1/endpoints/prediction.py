from typing import Any

from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException

from app import schemas, models, crud
from app.api import deps


router = APIRouter()


@router.post("/predict", response_model=schemas.Prediction)
def predict_image(
    *,
    db: Session = Depends(deps.get_db),
    image_in: schemas.PredictionCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:

    image_in.user_id = current_user.id
    prediction = crud.prediction.create(db, obj_in=image_in)
    return prediction
