from sqlalchemy import Column, Float, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base

def Activity(Base):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key = True)
    name = Column(String, nullable=False)
    activity_type = Column(Integer, ForeignKey('activitytype.id'), nullable=False)
    facility_id = Column(Integer, ForeignKey('facility.id'), nullable=False)
    prices = relationship('Price')
    image_url = Column(String(), nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.activity_type = kwargs.get('activity_type')
        self.facility_id = kwargs.get('facility_id')
        self.image_url = kwargs.get('image_url')


def ActivityType(Base):
    __tablename__ = 'activitytype'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')

  
