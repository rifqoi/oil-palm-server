from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import Field, Relationship, SQLModel, ARRAY, Float, Column

if TYPE_CHECKING:
    from app.models.prediction import Prediction


class Tree(SQLModel, table=True):
    @declared_attr
    def __tablename__(cls) -> str:
        return "trees"

    id: Optional[int] = Field(primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    prediction_id: int = Field(foreign_key="predictions.id")
    tree_id: Optional[int]
    lat: float
    long: float
    yolo_bbox: List[float] = Field(sa_column=Column(ARRAY(Float, dimensions=1)))
    coco_bbox: List[float] = Field(sa_column=Column(ARRAY(Float, dimensions=1)))
    nw_bounds: List[float] = Field(sa_column=Column(ARRAY(Float, dimensions=1)))
    se_bounds: List[float] = Field(sa_column=Column(ARRAY(Float, dimensions=1)))
    confidence: float
    prediction: Optional["Prediction"] = Relationship(back_populates="trees")

    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
