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
    Column("location", String()),
    Column("instructor", String()),
    Column("isCancelled", Boolean()),
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
