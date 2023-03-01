from datetime import datetime
from typing import List
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import Field, Relationship, SQLModel

from app.models.prediction import Prediction


class User(SQLModel, table=True):
    @declared_attr
    def __tablename__(cls) -> str:
        return "users"

    id: int = Field(primary_key=True, index=True)
    name: str = Field(max_length=256, nullable=False)
    username: str = Field(max_length=256, nullable=False)
    password: str = Field(max_length=256, nullable=False)
    predictions: List["Prediction"] = Relationship(back_populates="users")
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
