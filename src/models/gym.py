from sqlalchemy import Column, Float, String, Integer
from sqlalchemy.orm import relationship
from src.database import Base


class Gym(Base):
    """
    A building containing facilities.

    Attributes:
        - `id`              The ID of this gym (building).
        - `address`         The address of the buildling.
        - `facilities`      This gym's facilities.
        - `hours`           The building hours.
        - `image_url`       The URL of this gym's image.
        - `latitude`        The latitude coordinate of this gym.
        - `longitude`       The longitude coordinate of this gym.
        - `name`            The name of this gym.
    """

    __tablename__ = "gym"

    id = Column(Integer, primary_key=True)
    address = Column(String(1000), nullable=False)
    facilities = relationship("Facility")
    hours = relationship("OpenHours")
    image_url = Column(String(1000), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    name = Column(String(100), nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.address = kwargs.get("address")
        self.hours = kwargs.get("hours")
        self.image_url = kwargs.get("image_url")
        self.latitude = kwargs.get("latitude")
        self.longitude = kwargs.get("longitude")
        self.name = kwargs.get("name")

    def serialize(self):
        return {
            "id": self.id,
            "address": self.address,
            "facilities": self.facilities,
            "hours": self.hours,
            "image_url": self.image_url,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "name": self.name,
        }
