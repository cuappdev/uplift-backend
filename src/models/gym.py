from sqlalchemy import Column, Float, String, Integer
from sqlalchemy.orm import relationship
from src.database import Base
from src.models.openhours import OpenHours


class Gym(Base):
    """
    A building containing facilities.

    Attributes:
        - `id`              The ID of this gym (building).
        - `activities`      (nullable) The gym's activities.
        - `address`         The address of the buildling.
        - `amenities`       (nullable) This gym's amenities.
        - `facilities`      (nullable) This gym's facilities.
        - `hours`           (nullable) The building hours.
        - `activities`      (nullable) The gym's activities.
        - `image_url`       The URL of this gym's image.
        - `latitude`        The latitude coordinate of this gym.
        - `longitude`       The longitude coordinate of this gym.
        - `name`            The name of this gym.
    """

    __tablename__ = "gym"

    id = Column(Integer, primary_key=True)
    activities = relationship("Activity")
    address = Column(String, nullable=False)
    amenities = relationship("Amenity")
    facilities = relationship("Facility")
    hours = relationship("OpenHours")
    activities = relationship("Activity")
    image_url = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    name = Column(String, nullable=False)

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
