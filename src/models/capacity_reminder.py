from sqlalchemy import Column, Integer, ARRAY, Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLAEnum
from src.models.enums import DayOfWeekEnum, CapacityReminderGym
from src.database import Base

class CapacityReminder(Base):
    """
    A capacity reminder for an Uplift user.
    Attributes:
        - `id`                                    The ID of the capacity reminder.
        - `fcm_token`                             FCM token used to send notifications to the user's device.
        - `user_id`                               The ID of the user who owns this reminder.
        - `gyms`                                  The list of gyms the user wants to monitor for capacity.
        - `capacity_threshold`                    Notify user when gym capacity dips below this percentage.
        - `days_of_week`                          The days of the week when the reminder is active.
        - `is_active`                             Whether the reminder is currently active (default is True).
        - `reminder_schedule`                     The JSON for the schedule for capacity reminders based on day and time.
    """

    __tablename__ = "capacity_reminder"

    id = Column(Integer, primary_key=True)
    fcm_token = Column(String, nullable=False)
    gyms = Column(ARRAY(SQLAEnum(CapacityReminderGym)), nullable=False)
    capacity_threshold = Column(Integer, nullable=False)
    days_of_week = Column(ARRAY(SQLAEnum(DayOfWeekEnum)), nullable=False)
    is_active = Column(Boolean, default=True)
    reminder_schedule = Column(JSONB, nullable=False)
