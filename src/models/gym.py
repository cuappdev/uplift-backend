from sqlalchemy import Column, Float, String, Integer
from sqlalchemy.orm import relationship
from src.database import Base

class Gym(Base):
    __tablename__ = 'gym'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(1000), nullable=False)
    facilities = relationship("Facility")

    # TODO: - complete amenities table and scraper
    # # amenities = relationship('Amenity', cascade='delete, all')

    location=Column(String(1000), nullable=False)
    latitude=Column(Float, nullable=False)
    longitude=Column(Float, nullable=False)
    image_url = Column(String(1000), nullable=True)

    def __init__(self, **kwargs):
        self.id=kwargs.get("id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.location=kwargs.get("location")
        self.latitude = kwargs.get('latitude')
        self.longitude = kwargs.get('longitude')
        self.image_url = kwargs.get("image_url")

    def serialize(self):
        return {
            "id":self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "latitude": self.latitude,
            "longitude":self.longitude,
            "image_url": self.image_url
        }