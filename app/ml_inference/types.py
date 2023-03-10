from pydantic import BaseModel


class BoundingBox(BaseModel):
    # type: ignore
    x: float = None
    y: float = None
    width: float = None
    height: float = None
    confidence: float = None
    label: str = None

    # For mercator projection
    x_center: float = None
    y_center: float = None
