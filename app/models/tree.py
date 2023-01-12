from sqlalchemy import Integer, Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base_class import Base


class Tree(Base):
    id = Column(Integer, primary_key=True)
    lat = Column(Float)
    long = Column(Float)
    nw_bounds = Column(ARRAY(Float, dimensions=1))
    se_bounds = Column(ARRAY(Float, dimensions=1))
    confidence = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    users = relationship("User", back_populates="trees")
