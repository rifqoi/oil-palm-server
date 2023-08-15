from fastapi import APIRouter, middleware

from app.api.v1.endpoints import auth, prediction, area

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    prediction.router,
    prefix="/inference",
    tags=["inference", "ml-model"],
)
api_router.include_router(area.router, prefix="/areas", tags=["area", "geojson"])
