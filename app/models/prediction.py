from sqlalchemy import DateTime, Integer, Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from app.db.base_class import Base


class Prediction(Base):
    id = Column(Integer, primary_key=True)
    image_url = Column(String(256))
    count = Column(
        Integer,
    )
    yolo_bbox = Column(ARRAY(Float, dimensions=2))
    coco_bbox = Column(ARRAY(Float, dimensions=2))
    confidence = Column(ARRAY(Float, dimensions=1))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    users = relationship(
        "User",
        back_populates="predictions",
    )

    # bbox = [[1,1,1,1]]
    # prediction = [[60, 25, 15]] # Healthiness
