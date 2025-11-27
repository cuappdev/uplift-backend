from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime
from src.database import Base

class WeeklyChallenge(Base):
    """
    A weekly challenge.

    Attributes:
        - `id`              The ID of weekly challenge.
        - `name`            The name of weekly challenge.
        - `message`         The challenge's message.
        - `start_date`      The start date of the weekly challenge.
        - `end_date`        The end date of the weekly challenge.
    """
    __tablename__ = "weekly_challenge"

    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String, nullable = False)
    message = Column(String, nullable = False)
    start_date = Column(Date, nullable = False)
    end_date = Column (Date, nullable = False)


    def serialize(self):
        """
        Serialize weekly challenge object
        """
        return {
            "id": self.id,
            "name": self.name,
            "message": self.message,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat()
        }
    