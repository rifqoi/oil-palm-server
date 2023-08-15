from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import Field, Relationship, SQLModel, ARRAY, Float, Column


class Area(SQLModel, table=True):
    @declared_attr
    def __tablename__(cls) -> str:
        return "areas"

    id: Optional[int] = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")

    center_lat: float
    center_long: float

    geojson: str
    total_trees: Optional[int] = None

    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
