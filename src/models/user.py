from sqlalchemy import Column, Integer, Float, ForeignKey, String
from src.database import Base


class User(Base):
    """
    A user who enters a giveaway.

    Attributes:
        - `id`              The ID of user.
        - `net_id`          The user's Net ID.
        - `giveaway_id`     (nullable) The giveaway a user is entered into. //check this
    """
    
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)    
    net_id = Column(String, nullable=False)
    giveaway_id = Column(Integer, ForeignKey("giveaway.id"), nullable=True)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.net_id = kwargs.get("net_id")
        self.giveaway_id = kwargs.get("giveaways")

    def serialize(self):    
        return {        
            "id": self.id,        
            "net_id": self.net_id,
            "giveaway_id": self.giveaway_id
        }