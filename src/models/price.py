from database import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Price(Base):
  __tablename__ = "price"

  id = Column(Integer, primary_key=True)
  name = Column(String(), nullable=False)
  cost = Column(Integer, nullable=False)
  one_time = Column(Boolean, nullable=False)
  activity_id = Column(Integer, ForeignKey('activity.id'), nullable=False)

  def __init__(self, **kwargs):
    self.id = kwargs.get('id')
    self.name = kwargs.get("name")
    self.cost = kwargs.get("cost")
    self.one_time = kwargs.get("one_time")
    self.activity_id = kwargs.get('activity_id')

