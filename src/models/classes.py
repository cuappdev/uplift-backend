import datetime
from ..database import Base
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

class Class(Base):
    __tablename__ = "class"

    id = Column(Integer, primary_key=True)
    name = Column(String(), nullable=False)
    description = Column(String(), nullable=False)
    gyms = relationship("ClassInstance", back_populates="class_")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

class ClassInstance(Base):
    __tablename__ = "class_instance"

    id = Column(Integer, primary_key=True)
    gym_id = Column(Integer, ForeignKey("gym.id"), nullable=True)
    class_id = Column(Integer, ForeignKey("class.id"), nullable=False)
    location = Column(String(), nullable=False)
    instructor = Column(String(), nullable=False)
    isCanceled = Column(Boolean(), nullable=False, default=False)
    isVirtual = Column(Boolean(), nullable=False, default=False)
    start_time = Column(DateTime(), nullable=True)
    end_time = Column(DateTime(), nullable=True)

    class_ = relationship("Class", back_populates="gyms")
    gym = relationship("Gym", back_populates="classes")

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.gym_id = kwargs.get("gym_id")
        self.class_id = kwargs.get("class_id")
        self.location = kwargs.get("location")
        self.instructor = kwargs.get("instructor")
        self.isCanceled = kwargs.get("isCanceled")
        self.isVirtual = kwargs.get("isVirtual")
        self.start_time = kwargs.get("start_time")
        self.end_time = kwargs.get("end_time")

    def serialize(self):
        return {
            "id": self.id,
            "gym_id": self.gym_id,
            "class_id": self.class_id,
            "location": self.location,
            "instructor": self.instructor,
            "isCanceled": self.isCanceled,
            "isVirtual": self.isVirtual,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }
