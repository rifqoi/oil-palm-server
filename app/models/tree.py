from sqlalchemy import DateTime, Integer, Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base_class import Base
from sqlalchemy.sql import func


class Tree(Base):
    id = Column(Integer, primary_key=True)
    lat = Column(Float)
    long = Column(Float)
    nw_bounds = Column(ARRAY(Float, dimensions=1))
    se_bounds = Column(ARRAY(Float, dimensions=1))
    confidence = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    users = relationship("User", back_populates="trees")

    @property
    def formatted_created_at(self):
        return self.created_at.strftime("%Y-%m-%d")
