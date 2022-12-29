from io import BytesIO
import requests

from PIL import Image
from typing import Any

from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response

from app import schemas, models, crud
from app.api import deps
from app.core.config import settings


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

@router.post("/image",     responses = {
        200: {
            "content": {"image/png": {}}
        }
    })
def get_image(*, request: schemas.PredictionCreateRequest,     response_class=Response, current_user: models.User = Depends(deps.get_current_user)):
    url = f"https://maps.googleapis.com/maps/api/staticmap?center={request.lat},{request.long}&zoom=20&scale=3&size=640x640&maptype=satellite&key={settings.MAP_API_KEY}"
    try:
        response = requests.get(url=url)
        img = BytesIO(response.content)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

    return Response(content=img.getvalue(), media_type="image/png")