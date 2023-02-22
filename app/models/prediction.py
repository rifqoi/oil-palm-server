from sqlalchemy import DateTime, Identity, Integer, Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from app.db.base_class import Base


class Prediction(Base):
    id = Column(Integer, primary_key=True)
    # This id is exclusive for each user
    prediction_id = Column(Integer, Identity(start=1, cycle=True))
    image_url = Column(String(256))
    count = Column(
        Integer,
    )
    center_coords = Column(ARRAY(Float, dimensions=1))
    yolo_bbox = Column(ARRAY(Float, dimensions=2))
    coco_bbox = Column(ARRAY(Float, dimensions=2))
    nw_bounds = Column(ARRAY(Float, dimensions=1))
    se_bounds = Column(ARRAY(Float, dimensions=1))
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
