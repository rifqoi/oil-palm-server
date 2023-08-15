from typing import Any, Dict, Optional, Union
from datetime import datetime, timezone
from fastapi import HTTPException, status
from pydantic import BaseModel, validator
import geojson


class AreaInsert(BaseModel):
    center_lat: float
    center_long: float
    geojson: str

    @validator("geojson")
    def validate_geojson(cls, value):
        try:
            geojson_dict = geojson.loads(value)
            print(geojson_dict)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid geojson. {str(e)}",
            )

        return value


class AreaGet(BaseModel):
    id: int
    user_id: int
    center_lat: float
    center_long: float
    geojson: Union[str, Dict[str, Any]]
    total_trees: Optional[str]

    created_at: Optional[Union[datetime, str]]
    updated_at: Optional[Union[datetime, str]]
