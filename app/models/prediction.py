from sqlalchemy import Integer, Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base_class import Base


class Prediction(Base):
    id = Column(Integer, primary_key=True)
    image_url = Column(String(256))
    bounding_box = Column(ARRAY(Float, dimensions=2))
    confidence = Column(ARRAY(Float, dimensions=1))
    healthiness = Column(ARRAY(Float, dimensions=2))
    user_id = Column(Integer, ForeignKey("users.id"))
    users = relationship(
        "User",
        back_populates="predictions",
    )

    # bbox = [[1,1,1,1]]
    # prediction = [[60, 25, 15]] # Healthiness
