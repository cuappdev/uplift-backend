import datetime
from database import Base
from sqlalchemy import (
    Table,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    String,
    Boolean,
    func,
)
from sqlalchemy.orm import backref, relationship

classes_to_gyms = Table(
    "classes_to_gyms",
    Base.metadata,
    Column("id", primary_key=True),
    Column("gym_id", ForeignKey("gym.id")),
    Column("class_id", ForeignKey("class.id")),
    Column("start_time", DateTime()),
    Column("end_time", DateTime()),
)


class Class(Base):
    __tablename__ = "class"

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    description = Column(String(), nullable=False)
    gyms = relationship(
        "Gym",
        secondary=classes_to_gyms,
        back_populates="classes",  ##Change gym to rec_center
    )
    instructor = Column(String(), nullable=False)
    location = Column(String(), nullable=False)
    latitude = Column(Integer, nullable=False)
    longitude = Column(Float, nullable=False)
    dates = relationship("ClassTime", cascade="delete, all")
    isCancelled = Column(Boolean, nullable=False)
    preparation = Column(String(), nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.instructor = kwargs.get("instructor")
        self.location = kwargs.get("location")
        self.latitude = kwargs.get("latitude")
        self.longitude = kwargs.get("longitude")
        self.isCancelled = kwargs.get("isCancelled")
        self.preparation = kwargs.get("preparation")
        self.image_url = kwargs.get("image_url")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "instructor": self.description,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "isCancelled": self.isCancelled,
            "preparation": self.preparation,
            "image_url": self.image_url,
        }


class ClassTime(Base):
    __tablename__ = "classtime"

    id = Column(Integer, primary_key=True)
    daytime_id = Column(Integer, ForeignKey("daytime.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("class.id"), nullable=False)

    def __init__(self, **kwargs):
        self.daytime_id = kwargs.get("daytime_id")
        self.gym_id = kwargs.get("class_id")

    def serialize(self):
        return {"daytime_id": self.daytime_id, "class_id": self.class_id}
