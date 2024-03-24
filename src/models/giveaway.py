import enum
from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from src.database import Base
from src.models.user import User

class Giveaway(Base):
    """
    A giveaway object.

    Attributes:
        - `id`              The ID of the giveaway.
        - `name`            The name of the giveaway.
        - `user_ids`        (nullable) The IDs of users entered into this giveaway.
    """
    
    __tablename__ = "giveaway"

    id = Column(Integer, primary_key=True) 
    name = Column(String, nullable=False)
    user_ids = relationship(User)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.user_ids = kwargs.get("user_id")

    def serialize(self):    
        return {        
            "id": self.id,
            "name": self.name,
            "user_ids": self.user_ids
        }
