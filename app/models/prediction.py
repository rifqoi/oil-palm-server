from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import ARRAY, Column, Float, Identity, SQLModel, Relationship, Field


if TYPE_CHECKING:
    from app.models.tree import Tree
    from app.models.user import User


class Prediction(SQLModel, table=True):
    @declared_attr
    def __tablename__(cls) -> str:
        return "predictions"

    id: int = Field(primary_key=True)
    prediction_id: Optional[int] = Field()
    user_id: int = Field(foreign_key="users.id")
    image_url: str
    count: int
    center_coords: List[float] = Field(sa_column=Column(ARRAY(Float, dimensions=1)))
    nw_bounds: List[float] = Field(sa_column=Column(ARRAY(Float, dimensions=1)))
    se_bounds: List[float] = Field(sa_column=Column(ARRAY(Float, dimensions=1)))
    trees: List["Tree"] = Relationship(back_populates="prediction")
    users: Optional["User"] = Relationship(back_populates="predictions")
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
