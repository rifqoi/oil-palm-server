from sqlalchemy import DateTime, Integer, Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

# Import Prediction for sqlalchemy to detect the relationship
from app.models.prediction import Prediction
from app.models.tree import Tree


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256))
    name = Column(String(256))
    predictions = relationship(
        "Prediction",
        cascade="all,delete-orphan",
        back_populates="users",
        uselist=True,
    )
    trees = relationship(
        "Tree",
        cascade="all,delete-orphan",
        back_populates="users",
        uselist=True,
    )
    password = Column(String(256), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
