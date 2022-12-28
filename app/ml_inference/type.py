from typing import List

from pydantic import BaseModel

class BoundingBox(BaseModel):
    x: float = None
    y: float = None
    width: float = None
    height: float = None
    confidence: float = None
    label: str = None