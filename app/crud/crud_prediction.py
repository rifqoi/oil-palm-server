from typing import Optional

from app.crud.base import CRUDBase
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate, PredictionUpdate


class CRUDPrediction(CRUDBase[Prediction, PredictionCreate, PredictionUpdate]):
    ...


prediction = CRUDPrediction(Prediction)
