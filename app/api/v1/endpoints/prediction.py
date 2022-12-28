from typing import Any

from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException

from app import schemas, models, crud
from app.api import deps


router = APIRouter()


@router.post("/predict", status_code=201, response_model=schemas.PredictionCreate)
def predict_image(
    *,
    db: Session = Depends(deps.get_db),
    request: schemas.PredictionCreateRequest,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:

    try:
        prediction = crud.prediction.create(db, obj_in=request, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    return prediction