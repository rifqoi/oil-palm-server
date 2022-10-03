from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.api import api_router


app = FastAPI(title="OilPalm API")

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
